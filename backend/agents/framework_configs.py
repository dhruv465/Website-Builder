"""
Framework-specific deployment configurations for Vercel.

This module provides build settings and configurations for different
frontend frameworks including React, Vue, Next.js, and Svelte.
"""
from typing import Dict, Any, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class Framework(str, Enum):
    """Supported frontend frameworks."""
    VANILLA = "vanilla"
    REACT = "react"
    VUE = "vue"
    NEXTJS = "nextjs"
    SVELTE = "svelte"


class FrameworkBuildConfig(BaseModel):
    """Build configuration for a framework."""
    framework: Framework
    build_command: str = Field(..., description="Command to build the project")
    output_directory: str = Field(..., description="Directory containing build output")
    install_command: str = Field(default="npm install", description="Command to install dependencies")
    dev_command: Optional[str] = Field(None, description="Command to run dev server")
    environment_variables: Dict[str, str] = Field(default_factory=dict, description="Default environment variables")
    vercel_config: Dict[str, Any] = Field(default_factory=dict, description="Vercel-specific configuration")
    required_files: List[str] = Field(default_factory=list, description="Required files for deployment")
    
    class Config:
        use_enum_values = True


# Framework-specific configurations
FRAMEWORK_CONFIGS: Dict[Framework, FrameworkBuildConfig] = {
    Framework.VANILLA: FrameworkBuildConfig(
        framework=Framework.VANILLA,
        build_command="",  # No build needed for vanilla HTML
        output_directory=".",
        install_command="",
        dev_command="",
        required_files=["index.html"],
        vercel_config={
            "framework": None,  # Static site
        }
    ),
    
    Framework.REACT: FrameworkBuildConfig(
        framework=Framework.REACT,
        build_command="npm run build",
        output_directory="dist",
        install_command="npm install",
        dev_command="npm run dev",
        environment_variables={
            "NODE_ENV": "production",
        },
        required_files=["package.json", "index.html"],
        vercel_config={
            "framework": "vite",
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "installCommand": "npm install",
            "devCommand": "npm run dev",
            # SPA routing configuration
            "routes": [
                {
                    "src": "/[^.]+",
                    "dest": "/",
                    "status": 200
                }
            ],
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {
                            "key": "X-Content-Type-Options",
                            "value": "nosniff"
                        },
                        {
                            "key": "X-Frame-Options",
                            "value": "DENY"
                        },
                        {
                            "key": "X-XSS-Protection",
                            "value": "1; mode=block"
                        }
                    ]
                }
            ]
        }
    ),
    
    Framework.VUE: FrameworkBuildConfig(
        framework=Framework.VUE,
        build_command="npm run build",
        output_directory="dist",
        install_command="npm install",
        dev_command="npm run dev",
        environment_variables={
            "NODE_ENV": "production",
        },
        required_files=["package.json", "index.html"],
        vercel_config={
            "framework": "vite",
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "installCommand": "npm install",
            "devCommand": "npm run dev",
            # SPA routing configuration for Vue Router
            "routes": [
                {
                    "src": "/[^.]+",
                    "dest": "/",
                    "status": 200
                }
            ],
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {
                            "key": "X-Content-Type-Options",
                            "value": "nosniff"
                        },
                        {
                            "key": "X-Frame-Options",
                            "value": "DENY"
                        },
                        {
                            "key": "X-XSS-Protection",
                            "value": "1; mode=block"
                        }
                    ]
                }
            ]
        }
    ),
    
    Framework.NEXTJS: FrameworkBuildConfig(
        framework=Framework.NEXTJS,
        build_command="next build",
        output_directory=".next",
        install_command="npm install",
        dev_command="next dev",
        environment_variables={
            "NODE_ENV": "production",
        },
        required_files=["package.json", "next.config.js"],
        vercel_config={
            "framework": "nextjs",
            "buildCommand": "next build",
            "installCommand": "npm install",
            "devCommand": "next dev",
            # Next.js has native Vercel support, no custom routing needed
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {
                            "key": "X-Content-Type-Options",
                            "value": "nosniff"
                        },
                        {
                            "key": "X-Frame-Options",
                            "value": "DENY"
                        },
                        {
                            "key": "X-XSS-Protection",
                            "value": "1; mode=block"
                        }
                    ]
                }
            ]
        }
    ),
    
    Framework.SVELTE: FrameworkBuildConfig(
        framework=Framework.SVELTE,
        build_command="npm run build",
        output_directory="dist",
        install_command="npm install",
        dev_command="npm run dev",
        environment_variables={
            "NODE_ENV": "production",
        },
        required_files=["package.json"],
        vercel_config={
            "framework": "vite",
            "buildCommand": "npm run build",
            "outputDirectory": "dist",
            "installCommand": "npm install",
            "devCommand": "npm run dev",
            # SPA routing configuration for SvelteKit
            "routes": [
                {
                    "src": "/[^.]+",
                    "dest": "/",
                    "status": 200
                }
            ],
            "headers": [
                {
                    "source": "/(.*)",
                    "headers": [
                        {
                            "key": "X-Content-Type-Options",
                            "value": "nosniff"
                        },
                        {
                            "key": "X-Frame-Options",
                            "value": "DENY"
                        },
                        {
                            "key": "X-XSS-Protection",
                            "value": "1; mode=block"
                        }
                    ]
                }
            ]
        }
    ),
}


def get_framework_config(framework: Framework) -> FrameworkBuildConfig:
    """
    Get build configuration for a framework.
    
    Args:
        framework: Framework enum value
        
    Returns:
        FrameworkBuildConfig for the framework
        
    Raises:
        ValueError: If framework is not supported
    """
    if framework not in FRAMEWORK_CONFIGS:
        raise ValueError(f"Unsupported framework: {framework}")
    
    return FRAMEWORK_CONFIGS[framework]


def get_vercel_project_settings(
    framework: Framework,
    environment_variables: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Get Vercel project settings for a framework.
    
    Args:
        framework: Framework enum value
        environment_variables: Additional environment variables to include
        
    Returns:
        Dictionary of Vercel project settings
    """
    config = get_framework_config(framework)
    
    # Build project settings
    settings = {
        "framework": config.vercel_config.get("framework"),
    }
    
    # Add build settings if not vanilla
    if framework != Framework.VANILLA:
        settings["buildCommand"] = config.build_command
        settings["outputDirectory"] = config.output_directory
        settings["installCommand"] = config.install_command
        settings["devCommand"] = config.dev_command
    
    # Merge environment variables
    env_vars = {**config.environment_variables}
    if environment_variables:
        env_vars.update(environment_variables)
    
    if env_vars:
        # Convert to Vercel environment variable format
        settings["env"] = [
            {
                "key": key,
                "value": value,
                "target": ["production", "preview", "development"]
            }
            for key, value in env_vars.items()
        ]
    
    return settings


def get_vercel_config_json(framework: Framework) -> Dict[str, Any]:
    """
    Get vercel.json configuration for a framework.
    
    This configuration is used for routing and other deployment settings.
    
    Args:
        framework: Framework enum value
        
    Returns:
        Dictionary representing vercel.json content
    """
    config = get_framework_config(framework)
    
    vercel_json = {}
    
    # Add routes if specified
    if "routes" in config.vercel_config:
        vercel_json["routes"] = config.vercel_config["routes"]
    
    # Add headers if specified
    if "headers" in config.vercel_config:
        vercel_json["headers"] = config.vercel_config["headers"]
    
    # Add build configuration for non-vanilla frameworks
    if framework != Framework.VANILLA:
        vercel_json["buildCommand"] = config.build_command
        vercel_json["outputDirectory"] = config.output_directory
        vercel_json["installCommand"] = config.install_command
    
    return vercel_json


def validate_framework_files(framework: Framework, files: List[str]) -> tuple[bool, List[str]]:
    """
    Validate that required files are present for a framework.
    
    Args:
        framework: Framework enum value
        files: List of file paths in the deployment
        
    Returns:
        Tuple of (is_valid, missing_files)
    """
    config = get_framework_config(framework)
    missing_files = []
    
    for required_file in config.required_files:
        if required_file not in files:
            missing_files.append(required_file)
    
    is_valid = len(missing_files) == 0
    return is_valid, missing_files
