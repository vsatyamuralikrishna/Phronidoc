"""
Git utilities for automatic commits and pushes
"""

import subprocess
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)

# Repository root (parent of docs directory)
REPO_ROOT = Path(__file__).parent.parent.parent


def run_git_command(command: list, cwd: Optional[Path] = None) -> Tuple[bool, str, str]:
    """
    Run a git command and return success status, stdout, and stderr
    
    Args:
        command: List of command parts (e.g., ['git', 'add', 'file.md'])
        cwd: Working directory (defaults to repo root)
    
    Returns:
        Tuple of (success: bool, stdout: str, stderr: str)
    """
    if cwd is None:
        cwd = REPO_ROOT
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=30
        )
        success = result.returncode == 0
        return success, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        logger.error(f"Git command timed out: {' '.join(command)}")
        return False, "", "Command timed out"
    except Exception as e:
        logger.error(f"Error running git command: {e}")
        return False, "", str(e)


def is_git_repo() -> bool:
    """Check if the current directory is a git repository"""
    success, _, _ = run_git_command(['git', 'rev-parse', '--git-dir'])
    return success


def get_git_user_info() -> Tuple[Optional[str], Optional[str]]:
    """Get git user name and email from config"""
    name_success, name, _ = run_git_command(['git', 'config', 'user.name'])
    email_success, email, _ = run_git_command(['git', 'config', 'user.email'])
    
    git_name = name if name_success and name else None
    git_email = email if email_success and email else None
    
    return git_name, git_email


def git_add(file_path: Path) -> Tuple[bool, str]:
    """
    Stage a file for commit
    
    Args:
        file_path: Path to file relative to repo root or absolute path
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Convert to relative path from repo root
    try:
        if file_path.is_absolute():
            rel_path = file_path.relative_to(REPO_ROOT)
        else:
            rel_path = file_path
    except ValueError:
        # File is outside repo, use absolute path
        rel_path = file_path
    
    success, stdout, stderr = run_git_command(['git', 'add', str(rel_path)])
    
    if success:
        return True, f"Staged {rel_path}"
    else:
        return False, f"Failed to stage {rel_path}: {stderr}"


def git_commit(message: str, author_name: Optional[str] = None, author_email: Optional[str] = None) -> Tuple[bool, str]:
    """
    Create a git commit
    
    Args:
        message: Commit message
        author_name: Optional author name (uses git config if not provided)
        author_email: Optional author email (uses git config if not provided)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    commit_command = ['git', 'commit', '-m', message]
    
    # Add author if provided
    if author_name and author_email:
        commit_command.extend(['--author', f'{author_name} <{author_email}>'])
    
    success, stdout, stderr = run_git_command(commit_command)
    
    if success:
        return True, f"Committed: {message}"
    else:
        # Check if there's nothing to commit
        if "nothing to commit" in stderr.lower() or "nothing to commit" in stdout.lower():
            return True, "No changes to commit"
        return False, f"Failed to commit: {stderr}"


def git_push(remote: str = "origin", branch: str = "main") -> Tuple[bool, str]:
    """
    Push commits to remote repository
    
    Args:
        remote: Remote name (default: origin)
        branch: Branch name (default: main)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    # Try to get current branch if not specified
    if branch == "main":
        success, current_branch, _ = run_git_command(['git', 'branch', '--show-current'])
        if success and current_branch:
            branch = current_branch
    
    success, stdout, stderr = run_git_command(['git', 'push', remote, branch])
    
    if success:
        return True, f"Pushed to {remote}/{branch}"
    else:
        return False, f"Failed to push: {stderr}"


def git_status() -> dict:
    """Get git status information"""
    success, stdout, stderr = run_git_command(['git', 'status', '--porcelain'])
    
    if not success:
        return {"error": stderr}
    
    files = []
    for line in stdout.split('\n'):
        if line.strip():
            status = line[:2]
            filename = line[3:].strip()
            files.append({"status": status, "file": filename})
    
    return {"files": files, "has_changes": len(files) > 0}


def commit_and_push_file(
    file_path: Path,
    action: str = "update",
    custom_message: Optional[str] = None,
    push: bool = True
) -> Tuple[bool, str]:
    """
    Stage, commit, and optionally push a file
    
    Args:
        file_path: Path to the file
        action: Action type ('create', 'update', 'delete')
        custom_message: Custom commit message (optional)
        push: Whether to push to remote (default: True)
    
    Returns:
        Tuple of (success: bool, message: str)
    """
    if not is_git_repo():
        return False, "Not a git repository"
    
    # Get relative path for commit message
    try:
        rel_path = file_path.relative_to(REPO_ROOT)
    except ValueError:
        rel_path = file_path
    
    # Stage the file
    if action != "delete":
        add_success, add_msg = git_add(file_path)
        if not add_success:
            return False, add_msg
    else:
        # For deletes, we need to stage the deletion
        success, _, stderr = run_git_command(['git', 'rm', str(rel_path)])
        if not success:
            return False, f"Failed to stage deletion: {stderr}"
    
    # Create commit message
    if custom_message:
        commit_msg = custom_message
    else:
        action_messages = {
            "create": f"docs: Add {rel_path}",
            "update": f"docs: Update {rel_path}",
            "delete": f"docs: Delete {rel_path}"
        }
        commit_msg = action_messages.get(action, f"docs: {action} {rel_path}")
    
    # Commit
    commit_success, commit_msg_result = git_commit(commit_msg)
    if not commit_success:
        return False, commit_msg_result
    
    # Push if requested
    if push:
        push_success, push_msg = git_push()
        if not push_success:
            # Commit succeeded but push failed - return partial success
            return True, f"{commit_msg_result}. Push failed: {push_msg}"
        return True, f"{commit_msg_result}. {push_msg}"
    
    return True, commit_msg_result
