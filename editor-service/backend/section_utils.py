"""
Section management utilities for creating and managing documentation sections
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Base directory for documentation
DOCS_DIR = Path(__file__).parent.parent.parent / "docs"


def create_section(section_name: str, docs_dir: Optional[Path] = None) -> Tuple[bool, str, Path]:
    """
    Create a new top-level section
    
    Args:
        section_name: Name of the section (will be sanitized)
        docs_dir: Base docs directory (defaults to DOCS_DIR)
    
    Returns:
        Tuple of (success: bool, message: str, path: Path)
    """
    if docs_dir is None:
        docs_dir = DOCS_DIR
    
    # Sanitize section name
    sanitized_name = sanitize_name(section_name)
    if not sanitized_name:
        return False, "Invalid section name", Path()
    
    section_path = docs_dir / sanitized_name
    
    # Check if section already exists
    if section_path.exists():
        return False, f"Section '{sanitized_name}' already exists", section_path
    
    try:
        # Create directory
        section_path.mkdir(parents=True, exist_ok=True)
        
        # Create index.md
        index_path = section_path / "index.md"
        index_content = f"# {section_name}\n\nWelcome to the {section_name} documentation.\n\n## Overview\n\nAdd your documentation here.\n"
        index_path.write_text(index_content, encoding="utf-8")
        
        return True, f"Section '{sanitized_name}' created successfully", section_path
    except Exception as e:
        logger.error(f"Error creating section: {e}")
        return False, f"Failed to create section: {str(e)}", Path()


def create_subsection(section: str, subsection_name: str, docs_dir: Optional[Path] = None) -> Tuple[bool, str, Path]:
    """
    Create a sub-section within an existing section
    
    Args:
        section: Parent section name
        subsection_name: Name of the sub-section (will be sanitized)
        docs_dir: Base docs directory (defaults to DOCS_DIR)
    
    Returns:
        Tuple of (success: bool, message: str, path: Path)
    """
    if docs_dir is None:
        docs_dir = DOCS_DIR
    
    # Sanitize names
    sanitized_section = sanitize_name(section)
    sanitized_subsection = sanitize_name(subsection_name)
    
    if not sanitized_section or not sanitized_subsection:
        return False, "Invalid section or subsection name", Path()
    
    section_path = docs_dir / sanitized_section
    subsection_path = section_path / sanitized_subsection
    
    # Check if parent section exists
    if not section_path.exists():
        return False, f"Parent section '{sanitized_section}' does not exist", Path()
    
    # Check if subsection already exists
    if subsection_path.exists():
        return False, f"Sub-section '{sanitized_subsection}' already exists in '{sanitized_section}'", subsection_path
    
    try:
        # Create directory
        subsection_path.mkdir(parents=True, exist_ok=True)
        
        # Create index.md
        index_path = subsection_path / "index.md"
        index_content = f"# {subsection_name}\n\n## Overview\n\nAdd your {subsection_name} documentation here.\n"
        index_path.write_text(index_content, encoding="utf-8")
        
        return True, f"Sub-section '{sanitized_subsection}' created successfully", subsection_path
    except Exception as e:
        logger.error(f"Error creating subsection: {e}")
        return False, f"Failed to create subsection: {str(e)}", Path()


def get_section_structure(docs_dir: Optional[Path] = None) -> Dict:
    """
    Get the complete structure of sections and sub-sections
    
    Args:
        docs_dir: Base docs directory (defaults to DOCS_DIR)
    
    Returns:
        Dictionary with section structure
    """
    if docs_dir is None:
        docs_dir = DOCS_DIR
    
    structure = {
        "sections": [],
        "total_sections": 0,
        "total_documents": 0
    }
    
    if not docs_dir.exists():
        return structure
    
    # Get all top-level directories (sections)
    for item in docs_dir.iterdir():
        if item.is_dir() and not item.name.startswith(".") and item.name not in ["assets", "overrides"]:
            section_info = {
                "name": item.name,
                "path": str(item.relative_to(docs_dir)).replace("\\", "/"),
                "subsections": [],
                "documents": []
            }
            
            # Get sub-sections and documents
            for subitem in item.iterdir():
                if subitem.is_dir():
                    subsection_info = {
                        "name": subitem.name,
                        "path": str(subitem.relative_to(docs_dir)).replace("\\", "/"),
                        "documents": []
                    }
                    
                    # Get documents in sub-section
                    for doc in subitem.rglob("*.md"):
                        if doc.is_file():
                            rel_path = doc.relative_to(docs_dir)
                            subsection_info["documents"].append({
                                "name": doc.name,
                                "path": str(rel_path).replace("\\", "/")
                            })
                    
                    section_info["subsections"].append(subsection_info)
                elif subitem.is_file() and subitem.suffix == ".md":
                    rel_path = subitem.relative_to(docs_dir)
                    section_info["documents"].append({
                        "name": subitem.name,
                        "path": str(rel_path).replace("\\", "/")
                    })
            
            structure["sections"].append(section_info)
            structure["total_sections"] += 1
            structure["total_documents"] += len(section_info["documents"])
            for sub in section_info["subsections"]:
                structure["total_documents"] += len(sub["documents"])
    
    return structure


def delete_section(path: str, docs_dir: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Delete a section or sub-section
    
    Args:
        path: Relative path to section/sub-section (e.g., "engineering" or "engineering/api")
        docs_dir: Base docs directory (defaults to DOCS_DIR)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if docs_dir is None:
        docs_dir = DOCS_DIR
    
    path_clean = path.lstrip("/")
    full_path = docs_dir / path_clean
    
    # Security check - ensure path is within docs directory
    try:
        full_path.resolve().relative_to(docs_dir.resolve())
    except ValueError:
        return False, "Access denied: Path outside docs directory"
    
    if not full_path.exists():
        return False, f"Path '{path_clean}' does not exist"
    
    if not full_path.is_dir():
        return False, f"Path '{path_clean}' is not a directory"
    
    try:
        # Count files for commit message
        file_count = len(list(full_path.rglob("*")))
        
        # Remove directory and all contents
        import shutil
        shutil.rmtree(full_path)
        
        return True, f"Section '{path_clean}' deleted successfully ({file_count} files removed)"
    except Exception as e:
        logger.error(f"Error deleting section: {e}")
        return False, f"Failed to delete section: {str(e)}"


def sanitize_name(name: str) -> str:
    """
    Sanitize a section/sub-section name to be filesystem-safe
    
    Args:
        name: Original name
    
    Returns:
        Sanitized name
    """
    if not name:
        return ""
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Replace spaces with hyphens
    name = name.replace(" ", "-")
    
    # Remove invalid characters (keep alphanumeric, hyphens, underscores)
    import re
    name = re.sub(r'[^a-zA-Z0-9_-]', '', name)
    
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    # Convert to lowercase
    name = name.lower()
    
    return name


def get_section_path(section_name: str, docs_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Get the full path to a section
    
    Args:
        section_name: Section name
        docs_dir: Base docs directory (defaults to DOCS_DIR)
    
    Returns:
        Path object or None if not found
    """
    if docs_dir is None:
        docs_dir = DOCS_DIR
    
    sanitized = sanitize_name(section_name)
    section_path = docs_dir / sanitized
    
    if section_path.exists() and section_path.is_dir():
        return section_path
    
    return None
