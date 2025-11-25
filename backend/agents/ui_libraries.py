"""
UI Library cache for common packages (performance optimization).

This module provides a CACHE of the most popular UI libraries to avoid
repeated LLM calls. For any package not in this cache, the system will
use dynamic package research.

This is a PERFORMANCE OPTIMIZATION, not a limitation.
"""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class UILibrary(BaseModel):
    """Cached UI library definition (for performance)."""
    name: str
    description: str
    supported_frameworks: List[str]
    npm_packages: Dict[str, str]  # package_name: version
    setup_files: Dict[str, str]  # filename: content (only for complex setups)
    import_examples: Dict[str, str]  # component_type: import_statement
    usage_examples: Dict[str, str]  # component_type: usage_code
    configuration_required: bool = False
    setup_instructions: str = ""


class UILibraryRegistry:
    """
    Cache of popular UI libraries for performance optimization.
    
    This is NOT a limitation - any package not in this cache will be
    researched dynamically. This cache just makes common packages faster.
    """
    
    def __init__(self):
        """Initialize UI library cache."""
        self.libraries: Dict[str, UILibrary] = {}
        self._load_common_libraries()
    
    def _load_common_libraries(self):
        """Load most popular UI libraries (for performance)."""
        
        # Shadcn UI (React only) - Most popular
        self.libraries["shadcn"] = UILibrary(
            name="Shadcn UI",
            description="Beautifully designed components built with Radix UI and Tailwind CSS",
            supported_frameworks=["react", "nextjs"],
            npm_packages={
                "@radix-ui/react-slot": "^1.0.2",
                "@radix-ui/react-dialog": "^1.0.5",
                "class-variance-authority": "^0.7.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.2.0",
                "lucide-react": "^0.294.0"
            },
            setup_files={},  # LLM will generate these based on examples
            import_examples={
                "button": "import { Button } from '@/components/ui/button'",
                "card": "import { Card, CardHeader, CardContent } from '@/components/ui/card'"
            },
            usage_examples={
                "button": "<Button variant='default'>Click me</Button>",
                "card": "<Card><CardHeader>Title</CardHeader><CardContent>Content</CardContent></Card>"
            },
            configuration_required=True,
            setup_instructions="Requires Tailwind CSS and path aliases in tsconfig.json"
        )
        
        # Ant Design - Enterprise UI
        self.libraries["antd"] = UILibrary(
            name="Ant Design",
            description="Enterprise-class UI design language",
            supported_frameworks=["react", "nextjs", "vue"],
            npm_packages={"antd": "^5.12.0"},
            setup_files={},
            import_examples={
                "button": "import { Button } from 'antd'",
                "form": "import { Form, Input } from 'antd'"
            },
            usage_examples={
                "button": "<Button type='primary'>Click me</Button>",
                "form": "<Form><Form.Item label='Name'><Input /></Form.Item></Form>"
            },
            configuration_required=False,
            setup_instructions="Import Ant Design CSS in main file"
        )
        
        # Material UI - Google's Material Design
        self.libraries["mui"] = UILibrary(
            name="Material UI",
            description="Google's Material Design for React",
            supported_frameworks=["react", "nextjs"],
            npm_packages={
                "@mui/material": "^5.15.0",
                "@emotion/react": "^11.11.0",
                "@emotion/styled": "^11.11.0"
            },
            setup_files={},
            import_examples={
                "button": "import Button from '@mui/material/Button'",
                "card": "import { Card, CardContent } from '@mui/material'"
            },
            usage_examples={
                "button": "<Button variant='contained'>Click me</Button>",
                "card": "<Card><CardContent>Content</CardContent></Card>"
            },
            configuration_required=False,
            setup_instructions="Works out of the box"
        )
        
        # Chakra UI - Simple and accessible
        self.libraries["chakra"] = UILibrary(
            name="Chakra UI",
            description="Simple, modular and accessible components",
            supported_frameworks=["react", "nextjs"],
            npm_packages={
                "@chakra-ui/react": "^2.8.0",
                "@emotion/react": "^11.11.0",
                "@emotion/styled": "^11.11.0"
            },
            setup_files={},
            import_examples={
                "button": "import { Button } from '@chakra-ui/react'",
                "box": "import { Box } from '@chakra-ui/react'"
            },
            usage_examples={
                "button": "<Button colorScheme='blue'>Click me</Button>",
                "box": "<Box p={4}>Content</Box>"
            },
            configuration_required=True,
            setup_instructions="Wrap app with ChakraProvider"
        )
    
    def get_library(self, library_name: str) -> Optional[UILibrary]:
        """Get UI library by name."""
        return self.libraries.get(library_name.lower())
    
    def get_libraries_for_framework(self, framework: str) -> List[UILibrary]:
        """Get all UI libraries that support a specific framework."""
        return [
            lib for lib in self.libraries.values()
            if framework.lower() in lib.supported_frameworks
        ]
    
    def list_all_libraries(self) -> List[str]:
        """List all available UI library names."""
        return list(self.libraries.keys())
    
    def get_npm_packages(self, library_name: str) -> Dict[str, str]:
        """Get npm packages for a UI library."""
        library = self.get_library(library_name)
        return library.npm_packages if library else {}
    
    def get_setup_instructions(self, library_name: str) -> str:
        """Get setup instructions for a UI library."""
        library = self.get_library(library_name)
        return library.setup_instructions if library else ""
    
    def build_ui_library_prompt_addition(self, library_name: str, framework: str) -> str:
        """Build prompt addition for using a specific UI library."""
        library = self.get_library(library_name)
        if not library:
            return ""
        
        if framework.lower() not in library.supported_frameworks:
            return f"Note: {library.name} is not officially supported for {framework}"
        
        prompt = f"""
**UI Library: {library.name}**
{library.description}

**Import Examples:**
{chr(10).join(f"- {comp}: {imp}" for comp, imp in library.import_examples.items())}

**Usage Examples:**
{chr(10).join(f"- {comp}: {usage}" for comp, usage in library.usage_examples.items())}

**Setup Instructions:**
{library.setup_instructions}

**IMPORTANT:** Use {library.name} components throughout the application. Do NOT use plain HTML elements or Tailwind utility classes for UI components. Use the library's components instead.
"""
        return prompt


# Global UI library registry instance
ui_library_registry = UILibraryRegistry()
