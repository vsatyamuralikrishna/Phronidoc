"""
Phronidoc Documentation Editor Service
Backend API for editing and creating documentation
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from pathlib import Path
from datetime import datetime
import logging
from git_utils import commit_and_push_file, is_git_repo, git_status, commit_multiple_files
from section_utils import (
    create_section, create_subsection, get_section_structure,
    delete_section, DOCS_DIR as SECTION_DOCS_DIR
)
from mkdocs_utils import (
    read_navigation, add_section_to_nav, add_subsection_to_nav,
    remove_section_from_nav, remove_subsection_from_nav,
    validate_navigation
)
from config import get_docs_dir, get_mkdocs_config_path, get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load settings
settings = get_settings()

app = FastAPI(title="Phronidoc Documentation Editor API", version="1.0.0")

# CORS middleware to allow frontend to connect
cors_origins = settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory for documentation (from config or default)
DOCS_DIR = get_docs_dir()
MKDOCS_CONFIG = get_mkdocs_config_path()


class DocumentCreate(BaseModel):
    path: str  # e.g., "engineering/new-page.md"
    content: str
    title: Optional[str] = None
    commit_message: Optional[str] = None  # Optional custom commit message
    push: bool = True  # Whether to push to remote


class DocumentUpdate(BaseModel):
    content: str
    title: Optional[str] = None
    commit_message: Optional[str] = None  # Optional custom commit message
    push: bool = True  # Whether to push to remote


class DocumentInfo(BaseModel):
    path: str
    title: Optional[str] = None
    content: str
    last_modified: Optional[str] = None
    git_status: Optional[str] = None
    git_error: Optional[bool] = None


class SectionCreate(BaseModel):
    name: str
    commit_message: Optional[str] = None
    push: bool = True


class SubsectionCreate(BaseModel):
    name: str
    commit_message: Optional[str] = None
    push: bool = True


@app.get("/")
async def root():
    return {
        "message": "Phronidoc Documentation Editor API",
        "version": "1.0.0",
        "description": "Transforming team chaos into structural clarity. Phronidoc is an open-source knowledge architecture platform built for high-velocity teams who value documentation as a product."
    }


@app.get("/api/documents", response_model=List[dict])
async def list_documents():
    """List all markdown documents in the docs directory"""
    documents = []
    
    for md_file in DOCS_DIR.rglob("*.md"):
        relative_path = md_file.relative_to(DOCS_DIR)
        documents.append({
            "path": str(relative_path).replace("\\", "/"),
            "name": md_file.name,
            "directory": str(relative_path.parent).replace("\\", "/"),
            "size": md_file.stat().st_size,
            "last_modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
        })
    
    return sorted(documents, key=lambda x: x["path"])


@app.get("/api/documents/{file_path:path}", response_model=DocumentInfo)
async def get_document(file_path: str):
    """Get a specific document by path"""
    file_path_clean = file_path.lstrip("/")
    full_path = DOCS_DIR / file_path_clean
    
    # Security check - ensure file is within docs directory
    try:
        full_path.resolve().relative_to(DOCS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    if not full_path.suffix == ".md":
        raise HTTPException(status_code=400, detail="Only markdown files are supported")
    
    content = full_path.read_text(encoding="utf-8")
    stat = full_path.stat()
    
    # Extract title from content if available
    title = None
    if content.startswith("#"):
        title = content.split("\n")[0].lstrip("#").strip()
    
    return DocumentInfo(
        path=file_path_clean,
        title=title,
        content=content,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
    )


@app.post("/api/documents", response_model=DocumentInfo)
async def create_document(document: DocumentCreate):
    """Create a new document"""
    file_path_clean = document.path.lstrip("/")
    full_path = DOCS_DIR / file_path_clean
    
    # Security check
    try:
        full_path.resolve().relative_to(DOCS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Ensure it's a markdown file
    if not full_path.suffix == ".md":
        full_path = full_path.with_suffix(".md")
    
    # Create directory if it doesn't exist
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    if full_path.exists():
        raise HTTPException(status_code=409, detail="Document already exists")
    
    # Write content
    full_path.write_text(document.content, encoding="utf-8")
    
    # Git commit and push
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            git_success, git_message = commit_and_push_file(
                full_path,
                action="create",
                custom_message=document.commit_message,
                push=document.push
            )
            if not git_success:
                logger.warning(f"Git operation failed: {git_message}")
            else:
                logger.info(f"Git operation: {git_message}")
        except Exception as e:
            logger.error(f"Git operation exception: {e}", exc_info=True)
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    result = DocumentInfo(
        path=str(full_path.relative_to(DOCS_DIR)).replace("\\", "/"),
        title=document.title,
        content=document.content,
        last_modified=datetime.now().isoformat()
    )
    
    # Include git status in response
    if not git_success:
        logger.warning(f"Document created but git commit failed: {git_message}")
        result.git_error = True
        result.git_status = git_message
    else:
        result.git_status = git_message
    
    return result


@app.put("/api/documents/{file_path:path}", response_model=DocumentInfo)
async def update_document(file_path: str, document: DocumentUpdate):
    """Update an existing document"""
    file_path_clean = file_path.lstrip("/")
    full_path = DOCS_DIR / file_path_clean
    
    # Security check
    try:
        full_path.resolve().relative_to(DOCS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Write updated content
    full_path.write_text(document.content, encoding="utf-8")
    
    # Git commit and push
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            git_success, git_message = commit_and_push_file(
                full_path,
                action="update",
                custom_message=document.commit_message,
                push=document.push
            )
            if not git_success:
                logger.warning(f"Git operation failed: {git_message}")
            else:
                logger.info(f"Git operation: {git_message}")
        except Exception as e:
            logger.error(f"Git operation exception: {e}", exc_info=True)
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    stat = full_path.stat()
    
    result = DocumentInfo(
        path=file_path_clean,
        title=document.title,
        content=document.content,
        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
    )
    
    # Include git status in response
    if not git_success:
        logger.warning(f"Document updated but git commit failed: {git_message}")
        result.git_error = True
        result.git_status = git_message
    else:
        result.git_status = git_message
    
    return result


@app.delete("/api/documents/{file_path:path}")
async def delete_document(file_path: str):
    """Delete a document"""
    file_path_clean = file_path.lstrip("/")
    full_path = DOCS_DIR / file_path_clean
    
    # Security check
    try:
        full_path.resolve().relative_to(DOCS_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not full_path.exists():
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Store path for git before deletion
    file_for_git = full_path
    
    full_path.unlink()
    
    # Git commit and push
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            git_success, git_message = commit_and_push_file(
                file_for_git,
                action="delete",
                push=True  # Always push deletes
            )
            logger.info(f"Git operation: {git_message}")
        except Exception as e:
            logger.error(f"Git operation failed: {e}")
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    return {
        "message": "Document deleted successfully",
        "path": file_path_clean,
        "git_status": git_message if git_success else f"Warning: {git_message}"
    }


@app.get("/api/directories")
async def list_directories():
    """List all directories in the docs folder"""
    directories = []
    
    for item in DOCS_DIR.rglob("*"):
        if item.is_dir() and not item.name.startswith("."):
            relative_path = item.relative_to(DOCS_DIR)
            directories.append({
                "path": str(relative_path).replace("\\", "/"),
                "name": item.name
            })
    
    return sorted(directories, key=lambda x: x["path"])


@app.get("/api/mkdocs-config")
async def get_mkdocs_config():
    """Get the current mkdocs.yml configuration"""
    if not MKDOCS_CONFIG.exists():
        raise HTTPException(status_code=404, detail="mkdocs.yml not found")
    
    return {"config": MKDOCS_CONFIG.read_text(encoding="utf-8")}


@app.get("/api/git/status")
async def get_git_status():
    """Get git repository status"""
    if not is_git_repo():
        return {"is_repo": False, "message": "Not a git repository"}
    
    status = git_status()
    return {"is_repo": True, **status}


# Section Management Endpoints

@app.get("/api/sections")
async def list_sections():
    """Get the complete section structure"""
    structure = get_section_structure(DOCS_DIR)
    return structure


@app.post("/api/sections")
async def create_section_endpoint(section: SectionCreate):
    """Create a new top-level section"""
    # Create section folder and index.md
    success, message, section_path = create_section(section.name, DOCS_DIR)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Update mkdocs.yml navigation
    nav_success = add_section_to_nav(
        section.name,
        section_path.relative_to(DOCS_DIR).as_posix(),
        MKDOCS_CONFIG
    )
    
    if not nav_success:
        logger.warning(f"Section created but navigation update failed: {section.name}")
    
    # Git commit and push
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            # Stage section folder and mkdocs.yml
            files_to_commit = [
                section_path / "index.md",
                MKDOCS_CONFIG
            ]
            
            commit_msg = section.commit_message or f"docs: Add section '{section.name}'"
            git_success, git_message = commit_multiple_files(
                files_to_commit,
                commit_msg,
                push=section.push
            )
            if not git_success:
                logger.warning(f"Git operation failed: {git_message}")
            else:
                logger.info(f"Git operation: {git_message}")
        except Exception as e:
            logger.error(f"Git operation exception: {e}", exc_info=True)
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    response = {
        "message": message,
        "path": str(section_path.relative_to(DOCS_DIR)).replace("\\", "/"),
        "navigation_updated": nav_success
    }
    
    # Always include git status, even if it failed
    if git_success:
        response["git_status"] = git_message
    else:
        response["git_status"] = f"Warning: {git_message}"
        response["git_error"] = True
    
    return response


@app.post("/api/sections/{section_name}/subsections")
async def create_subsection_endpoint(section_name: str, subsection: SubsectionCreate):
    """Create a sub-section within an existing section"""
    # Create sub-section folder and index.md
    success, message, subsection_path = create_subsection(section_name, subsection.name, DOCS_DIR)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Update mkdocs.yml navigation
    nav_success = add_subsection_to_nav(
        section_name,
        subsection.name,
        subsection_path.relative_to(DOCS_DIR).as_posix(),
        MKDOCS_CONFIG
    )
    
    if not nav_success:
        logger.warning(f"Sub-section created but navigation update failed: {section_name}/{subsection.name}")
    
    # Git commit and push
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            # Stage sub-section folder and mkdocs.yml
            files_to_commit = [
                subsection_path / "index.md",
                MKDOCS_CONFIG
            ]
            
            commit_msg = subsection.commit_message or f"docs: Add subsection '{subsection.name}' to '{section_name}'"
            git_success, git_message = commit_multiple_files(
                files_to_commit,
                commit_msg,
                push=subsection.push
            )
            logger.info(f"Git operation: {git_message}")
        except Exception as e:
            logger.error(f"Git operation failed: {e}")
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    return {
        "message": message,
        "path": str(subsection_path.relative_to(DOCS_DIR)).replace("\\", "/"),
        "navigation_updated": nav_success,
        "git_status": git_message if git_success else f"Warning: {git_message}"
    }


@app.delete("/api/sections/{path:path}")
async def delete_section_endpoint(path: str):
    """Delete a section or sub-section"""
    # Delete section folder
    success, message = delete_section(path, DOCS_DIR)
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Determine if it's a section or sub-section
    path_parts = path.strip("/").split("/")
    is_subsection = len(path_parts) > 1
    
    # Update mkdocs.yml navigation
    nav_success = False
    if is_subsection:
        section_name = path_parts[0]
        subsection_name = path_parts[1]
        nav_success = remove_subsection_from_nav(section_name, subsection_name, MKDOCS_CONFIG)
    else:
        section_name = path_parts[0]
        nav_success = remove_section_from_nav(section_name, MKDOCS_CONFIG)
    
    if not nav_success:
        logger.warning(f"Section deleted but navigation update failed: {path}")
    
    # Git commit and push
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            from git_utils import run_git_command, git_commit, git_push, REPO_ROOT
            
            # Stage all changes (deletion and mkdocs.yml update)
            run_git_command(['git', 'add', '-A'], cwd=REPO_ROOT)
            
            # Commit
            commit_msg = f"docs: Delete section '{path}'"
            commit_success, commit_result = git_commit(commit_msg)
            
            if commit_success:
                # Push
                push_success, push_result = git_push()
                git_message = f"{commit_result}. {push_result}" if push_success else f"{commit_result}. Push failed: {push_result}"
                git_success = push_success
            else:
                git_success = False
                git_message = commit_result
            
            logger.info(f"Git operation: {git_message}")
        except Exception as e:
            logger.error(f"Git operation failed: {e}")
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    return {
        "message": message,
        "path": path,
        "navigation_updated": nav_success,
        "git_status": git_message if git_success else f"Warning: {git_message}"
    }


@app.get("/api/navigation")
async def get_navigation():
    """Get the current navigation structure from mkdocs.yml"""
    nav_data = read_navigation(MKDOCS_CONFIG)
    return {
        "navigation": nav_data.get("nav", []),
        "config_path": str(MKDOCS_CONFIG)
    }


@app.put("/api/navigation")
async def update_navigation_endpoint(nav_structure: dict):
    """Manually update the navigation structure"""
    from mkdocs_utils import update_navigation
    
    nav_list = nav_structure.get("navigation", [])
    success = update_navigation(nav_list, MKDOCS_CONFIG)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update navigation")
    
    # Git commit
    git_success = True
    git_message = ""
    if is_git_repo():
        try:
            git_success, git_message = commit_and_push_file(
                MKDOCS_CONFIG,
                action="update",
                custom_message="docs: Update navigation structure",
                push=True
            )
        except Exception as e:
            logger.error(f"Git operation failed: {e}")
            git_success = False
            git_message = f"Git error: {str(e)}"
    
    return {
        "message": "Navigation updated successfully",
        "git_status": git_message if git_success else f"Warning: {git_message}"
    }


@app.get("/api/navigation/validate")
async def validate_navigation_endpoint():
    """Validate the navigation structure"""
    validation = validate_navigation(MKDOCS_CONFIG, DOCS_DIR)
    return validation


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
