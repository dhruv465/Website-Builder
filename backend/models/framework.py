"""
Framework-related models for multi-framework support.

This module contains:
- FrameworkType enum for supported frameworks
- ModernDesignStyle enum for 2025 design trends
- GeneratedFile model for individual generated files
- GeneratedProject model for complete project structure
"""
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class FrameworkType(str, Enum):
    """Supported framework types."""
    VANILLA_HTML = "vanilla-html"
    REACT = "react"
    VUE = "vue"
    NEXTJS = "nextjs"
    SVELTE = "svelte"


class ModernDesignStyle(str, Enum):
    """Modern design styles for 2025."""
    BOLD_MINIMALISM = "bold-minimalism"
    NEO_BRUTALISM = "neo-brutalism"
    FLAT_MINIMAL = "flat-minimal"
    ANTI_DESIGN = "anti-design"
    BIG_BLOCKS = "big-blocks"
    ORGANIC_FLUID = "organic-fluid"
    RETRO_NOSTALGIC = "retro-nostalgic"
    EXPERIMENTAL_NAV = "experimental-nav"
    EXPRESSIVE_TYPOGRAPHY = "expressive-typography"


class GeneratedFile(BaseModel):
    """Model for a single generated file."""
    path: str = Field(..., description="Relative path of the file in the project")
    content: str = Field(..., description="File content")
    file_type: str = Field(..., description="File type (e.g., 'js', 'jsx', 'tsx', 'css', 'html', 'json')")
    description: Optional[str] = Field(None, description="Description of the file's purpose")
    
    class Config:
        json_schema_extra = {
            "example": {
                "path": "src/components/Header.jsx",
                "content": "import React from 'react';\n\nexport default function Header() {\n  return <header>...</header>;\n}",
                "file_type": "jsx",
                "description": "Main header component"
            }
        }


class GeneratedProject(BaseModel):
    """Model for a complete generated project."""
    framework: FrameworkType = Field(..., description="Framework used for the project")
    files: List[GeneratedFile] = Field(default_factory=list, description="List of generated files")
    package_json: Optional[Dict[str, Any]] = Field(None, description="package.json content")
    config_files: Dict[str, str] = Field(
        default_factory=dict,
        description="Configuration files (e.g., vite.config.js, tsconfig.json)"
    )
    dependencies: Dict[str, str] = Field(
        default_factory=dict,
        description="Project dependencies with versions"
    )
    dev_dependencies: Dict[str, str] = Field(
        default_factory=dict,
        description="Development dependencies with versions"
    )
    readme: Optional[str] = Field(None, description="README.md content")
    project_name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "framework": "react",
                "files": [],
                "package_json": {
                    "name": "my-react-app",
                    "version": "1.0.0",
                    "type": "module"
                },
                "config_files": {
                    "vite.config.js": "export default { ... }"
                },
                "dependencies": {
                    "react": "^18.2.0",
                    "react-dom": "^18.2.0"
                },
                "dev_dependencies": {
                    "vite": "^5.0.0"
                },
                "project_name": "my-react-app",
                "description": "A React application"
            }
        }


class CodeMetadata(BaseModel):
    """Extended metadata for generated code with framework information."""
    framework: FrameworkType = Field(default=FrameworkType.VANILLA_HTML, description="Framework used")
    dependencies: List[str] = Field(default_factory=list, description="List of dependencies")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    has_tailwind: bool = Field(default=False, description="Whether Tailwind CSS is included")
    has_responsive_design: bool = Field(default=False, description="Whether responsive design is implemented")
    has_meta_tags: bool = Field(default=False, description="Whether SEO meta tags are included")
    page_count: int = Field(default=1, description="Number of pages/routes")
    has_typescript: bool = Field(default=False, description="Whether TypeScript is used")
    has_testing: bool = Field(default=False, description="Whether testing setup is included")
    design_style: Optional[ModernDesignStyle] = Field(None, description="Applied design style")
    
    class Config:
        json_schema_extra = {
            "example": {
                "framework": "react",
                "dependencies": ["react", "react-dom", "react-router-dom"],
                "has_tailwind": True,
                "has_responsive_design": True,
                "has_meta_tags": True,
                "page_count": 3,
                "has_typescript": True,
                "has_testing": False,
                "design_style": "bold-minimalism"
            }
        }
