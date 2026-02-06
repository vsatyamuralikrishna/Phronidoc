"""
Configuration management for Phronidoc editor service
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Documentation directory
    docs_dir: Optional[str] = None
    
    # Git configuration
    git_repo_path: Optional[str] = None
    git_remote: Optional[str] = None
    git_branch: Optional[str] = None
    
    # MkDocs configuration
    mkdocs_config_path: Optional[str] = None
    
    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8001
    
    # CORS
    cors_origins: str = "*"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def get_docs_dir() -> Path:
    """Get the documentation directory path"""
    settings = Settings()
    
    if settings.docs_dir:
        return Path(settings.docs_dir)
    
    # Default: parent of editor-service/backend
    return Path(__file__).parent.parent.parent / "docs"


def get_mkdocs_config_path() -> Path:
    """Get the mkdocs.yml path"""
    settings = Settings()
    
    if settings.mkdocs_config_path:
        return Path(settings.mkdocs_config_path)
    
    # Default: parent of editor-service/backend
    return Path(__file__).parent.parent.parent / "mkdocs.yml"


def get_git_repo_path() -> Path:
    """Get the git repository root path"""
    settings = Settings()
    
    if settings.git_repo_path:
        return Path(settings.git_repo_path)
    
    # Default: parent of editor-service/backend
    return Path(__file__).parent.parent.parent


def get_settings() -> Settings:
    """Get application settings"""
    return Settings()
