"""
MkDocs configuration management utilities
"""

import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import copy

logger = logging.getLogger(__name__)

# Path to mkdocs.yml
MKDOCS_CONFIG = Path(__file__).parent.parent.parent / "mkdocs.yml"


def read_navigation(mkdocs_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Read and parse the navigation structure from mkdocs.yml
    
    Args:
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        Dictionary containing navigation structure
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    if not mkdocs_path.exists():
        logger.error(f"mkdocs.yml not found at {mkdocs_path}")
        return {"nav": []}
    
    try:
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return {
            "nav": config.get("nav", []),
            "full_config": config
        }
    except Exception as e:
        logger.error(f"Error reading mkdocs.yml: {e}")
        return {"nav": []}


def add_section_to_nav(section_name: str, section_path: str, mkdocs_path: Optional[Path] = None) -> bool:
    """
    Add a new section to the navigation
    
    Args:
        section_name: Display name for the section
        section_path: Path to section index (e.g., "engineering/index.md")
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        True if successful, False otherwise
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    try:
        # Read current config
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if "nav" not in config:
            config["nav"] = []
        
        # Check if section already exists
        nav = config["nav"]
        for item in nav:
            if isinstance(item, dict) and section_name in item:
                logger.warning(f"Section '{section_name}' already in navigation")
                return False
        
        # Add new section
        nav.append({section_name: f"{section_path}/index.md"})
        
        # Write back
        write_mkdocs_config(config, mkdocs_path)
        
        return True
    except Exception as e:
        logger.error(f"Error adding section to navigation: {e}")
        return False


def add_subsection_to_nav(
    section: str,
    subsection_name: str,
    subsection_path: str,
    mkdocs_path: Optional[Path] = None
) -> bool:
    """
    Add a sub-section to an existing section in navigation
    
    Args:
        section: Parent section name
        subsection_name: Display name for sub-section
        subsection_path: Path to sub-section (e.g., "engineering/api")
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        True if successful, False otherwise
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    try:
        # Read current config
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if "nav" not in config:
            config["nav"] = []
        
        nav = config["nav"]
        
        # Find the parent section
        for item in nav:
            if isinstance(item, dict) and section in item:
                section_nav = item[section]
                
                # If section nav is a string, convert to list
                if isinstance(section_nav, str):
                    section_nav = [{"Overview": section_nav}]
                    item[section] = section_nav
                
                # Check if subsection already exists
                for sub_item in section_nav:
                    if isinstance(sub_item, dict) and subsection_name in sub_item:
                        logger.warning(f"Sub-section '{subsection_name}' already in navigation")
                        return False
                
                # Add sub-section
                section_nav.append({subsection_name: f"{subsection_path}/index.md"})
                
                # Write back
                write_mkdocs_config(config, mkdocs_path)
                return True
        
        logger.warning(f"Parent section '{section}' not found in navigation")
        return False
    except Exception as e:
        logger.error(f"Error adding subsection to navigation: {e}")
        return False


def update_navigation(nav_structure: List[Any], mkdocs_path: Optional[Path] = None) -> bool:
    """
    Replace the entire navigation structure
    
    Args:
        nav_structure: New navigation structure (list)
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        True if successful, False otherwise
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    try:
        # Read current config
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Update navigation
        config["nav"] = nav_structure
        
        # Write back
        write_mkdocs_config(config, mkdocs_path)
        
        return True
    except Exception as e:
        logger.error(f"Error updating navigation: {e}")
        return False


def validate_navigation(mkdocs_path: Optional[Path] = None, docs_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Validate that all navigation entries point to existing files
    
    Args:
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
        docs_dir: Base docs directory
    
    Returns:
        Dictionary with validation results
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    if docs_dir is None:
        docs_dir = Path(__file__).parent.parent.parent / "docs"
    
    result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "orphaned": []
    }
    
    try:
        nav_data = read_navigation(mkdocs_path)
        nav = nav_data.get("nav", [])
        
        def validate_nav_item(item: Any, path_prefix: str = ""):
            """Recursively validate navigation items"""
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, str):
                        # It's a file path
                        file_path = docs_dir / value
                        if not file_path.exists():
                            result["valid"] = False
                            result["errors"].append(f"Navigation item '{key}' points to non-existent file: {value}")
                    elif isinstance(value, list):
                        # It's a nested structure
                        validate_nav_item(value, f"{path_prefix}/{key}")
            elif isinstance(item, list):
                for sub_item in item:
                    validate_nav_item(sub_item, path_prefix)
            elif isinstance(item, str):
                # Direct file reference
                file_path = docs_dir / item
                if not file_path.exists():
                    result["warnings"].append(f"File not found: {item}")
        
        validate_nav_item(nav)
        
    except Exception as e:
        logger.error(f"Error validating navigation: {e}")
        result["valid"] = False
        result["errors"].append(f"Validation error: {str(e)}")
    
    return result


def write_mkdocs_config(config: Dict[str, Any], mkdocs_path: Optional[Path] = None) -> bool:
    """
    Write configuration back to mkdocs.yml with proper formatting
    
    Args:
        config: Configuration dictionary
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        True if successful, False otherwise
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    try:
        # Write updated config with proper YAML formatting
        with open(mkdocs_path, 'w', encoding='utf-8') as f:
            yaml.dump(
                config,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
                indent=2,
                width=1000
            )
        
        return True
    except Exception as e:
        logger.error(f"Error writing mkdocs.yml: {e}")
        return False


def remove_section_from_nav(section_name: str, mkdocs_path: Optional[Path] = None) -> bool:
    """
    Remove a section from navigation
    
    Args:
        section_name: Name of section to remove
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        True if successful, False otherwise
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    try:
        # Read current config
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if "nav" not in config:
            return False
        
        nav = config["nav"]
        
        # Remove section
        config["nav"] = [item for item in nav if not (isinstance(item, dict) and section_name in item)]
        
        # Write back
        write_mkdocs_config(config, mkdocs_path)
        
        return True
    except Exception as e:
        logger.error(f"Error removing section from navigation: {e}")
        return False


def remove_subsection_from_nav(section: str, subsection_name: str, mkdocs_path: Optional[Path] = None) -> bool:
    """
    Remove a sub-section from navigation
    
    Args:
        section: Parent section name
        subsection_name: Sub-section name to remove
        mkdocs_path: Path to mkdocs.yml (defaults to MKDOCS_CONFIG)
    
    Returns:
        True if successful, False otherwise
    """
    if mkdocs_path is None:
        mkdocs_path = MKDOCS_CONFIG
    
    try:
        # Read current config
        with open(mkdocs_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if "nav" not in config:
            return False
        
        nav = config["nav"]
        
        # Find and update parent section
        for item in nav:
            if isinstance(item, dict) and section in item:
                section_nav = item[section]
                
                if isinstance(section_nav, list):
                    # Remove subsection
                    item[section] = [
                        sub_item for sub_item in section_nav
                        if not (isinstance(sub_item, dict) and subsection_name in sub_item)
                    ]
                
                # Write back
                write_mkdocs_config(config, mkdocs_path)
                return True
        
        return False
    except Exception as e:
        logger.error(f"Error removing subsection from navigation: {e}")
        return False
