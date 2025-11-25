"""
Code Generation Agent for generating HTML/CSS/JS code from requirements.

This agent:
- Generates complete, production-ready HTML/CSS/JS code
- Validates HTML syntax and structure
- Ensures responsive design patterns
- Verifies meta tags and SEO elements
- Checks for Tailwind CSS CDN inclusion
- Calculates confidence scores for generated code
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import re
import difflib

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from agents.templates import template_library, SiteTemplate
from agents.design_styles import design_style_library, DesignStyle
from agents.ui_libraries import ui_library_registry, UILibrary
from agents.package_research_agent import package_research_agent, PackageResearchInput
from services.gemini_service import gemini_service
from utils.logging import logger


# Input Models
class CodeGenerationInput(AgentInput):
    """Input for code generation."""
    requirements: Dict[str, Any] = Field(..., description="Site requirements from Input Agent")
    existing_code: Optional[str] = Field(None, description="Existing code for modifications")
    modifications: Optional[List[str]] = Field(None, description="Specific changes requested")
    template_preference: Optional[str] = Field(None, description="Preferred template to use")
    framework: Optional[str] = Field("vanilla", description="Framework to use (vanilla, react, vue, nextjs, svelte)")
    ui_library: Optional[str] = Field(None, description="UI library to use (shadcn, antd, mui, chakra, mantine, vuetify, primevue, daisyui)")


# Output Models
class CodeMetadata(BaseModel):
    """Metadata about generated code."""
    framework: str = "vanilla"
    dependencies: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    has_tailwind: bool = False
    has_responsive_design: bool = False
    has_meta_tags: bool = False
    page_count: int = 1
    build_config: Optional[Dict[str, Any]] = None


class CodeValidation(BaseModel):
    """Validation results for generated code."""
    is_valid_html: bool = True
    has_title: bool = False
    has_description: bool = False
    has_viewport: bool = False
    has_tailwind_cdn: bool = False
    has_responsive_patterns: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class GeneratedCode(BaseModel):
    """Generated code output."""
    html: str = Field(..., description="Generated HTML code or main entry file")
    additional_files: Optional[Dict[str, str]] = Field(None, description="Additional files for multi-file frameworks")
    metadata: CodeMetadata = Field(default_factory=CodeMetadata)
    validation: CodeValidation = Field(default_factory=CodeValidation)


class CodeDiff(BaseModel):
    """Diff information for code modifications."""
    added_lines: int = 0
    removed_lines: int = 0
    modified_sections: List[str] = Field(default_factory=list)
    diff_summary: str = ""


class CodeGenerationOutput(AgentOutput):
    """Output for code generation."""
    generated_code: Optional[GeneratedCode] = None
    template_used: Optional[str] = None
    is_modification: bool = False
    code_diff: Optional[CodeDiff] = None


class CodeGenerationAgent(BaseAgent):
    """
    Code Generation Agent for creating website code.
    
    Responsibilities:
    - Generate HTML/CSS/JS code from requirements
    - Validate HTML syntax and structure
    - Ensure responsive design patterns
    - Verify SEO meta tags
    - Calculate confidence scores
    """
    
    def __init__(self):
        """Initialize Code Generation Agent."""
        super().__init__(name="CodeGenerationAgent")
        self.gemini = gemini_service
        self.template_library = template_library  # For vanilla HTML only
        self.design_style_library = design_style_library
        self.ui_library_registry = ui_library_registry  # Cache for common packages
        self.package_research_agent = package_research_agent  # Dynamic research
        logger.info("Code Generation Agent initialized")
    
    async def _research_and_get_ui_library_info(
        self,
        ui_library: str,
        framework: str,
        context: AgentContext
    ) -> Dict[str, Any]:
        """
        Research a UI library dynamically if not in registry.
        
        Args:
            ui_library: Name of the UI library
            framework: Framework being used
            context: Execution context
            
        Returns:
            Dictionary with UI library information
        """
        # First check if it's in our registry
        known_library = self.ui_library_registry.get_library(ui_library)
        if known_library:
            logger.info(f"Using known UI library: {ui_library}")
            return {
                "npm_packages": known_library.npm_packages,
                "setup_files": known_library.setup_files,
                "prompt_addition": self.ui_library_registry.build_ui_library_prompt_addition(ui_library, framework),
                "is_known": True
            }
        
        # If not known, research it dynamically
        logger.info(f"Researching unknown UI library: {ui_library}")
        research_input = PackageResearchInput(
            package_name=ui_library,
            framework=framework,
            use_case="UI component library for building user interfaces"
        )
        
        research_output = await self.package_research_agent.execute(research_input, context)
        
        if not research_output.success or not research_output.package_info:
            logger.warning(f"Failed to research {ui_library}, falling back to Tailwind")
            return {
                "npm_packages": {},
                "setup_files": {},
                "prompt_addition": "",
                "is_known": False,
                "warnings": [f"Could not find information about '{ui_library}', using Tailwind CSS instead"]
            }
        
        package_info = research_output.package_info
        
        # Build npm packages dict
        npm_packages = {package_info.package_name: package_info.version}
        for peer_dep in package_info.peer_dependencies:
            if peer_dep.strip() and peer_dep.strip() not in ['react', 'react-dom', 'vue', 'next']:
                npm_packages[peer_dep.strip()] = "latest"
        
        # Build prompt addition
        prompt_addition = f"""
**UI Library: {package_info.package_name}**
{package_info.description}

**Installation:** {package_info.installation_command}

**Import Examples:**
{chr(10).join(f"- {imp}" for imp in package_info.import_examples)}

**Usage Examples:**
{chr(10).join(f"- {usage}" for usage in package_info.usage_examples)}

**Configuration Required:** {'Yes' if package_info.configuration_required else 'No'}
{chr(10).join(f"- {step}" for step in package_info.configuration_steps) if package_info.configuration_steps else ''}

**Best Practices:**
{chr(10).join(f"- {practice}" for practice in package_info.best_practices)}

**IMPORTANT:** Use {package_info.package_name} components throughout the application. Follow the import and usage examples above.
"""
        
        return {
            "npm_packages": npm_packages,
            "setup_files": package_info.setup_files,
            "prompt_addition": prompt_addition,
            "is_known": False,
            "warnings": research_output.warnings,
            "package_info": package_info
        }
        
        logger.info("Code Generation Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute code generation.
        
        Args:
            input_data: Input data with requirements
            context: Execution context
            
        Returns:
            CodeGenerationOutput with generated code
            
        Raises:
            AgentError: If code generation fails
        """
        try:
            if not isinstance(input_data, CodeGenerationInput):
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            # Generate code
            is_modification = False
            code_diff = None
            
            if input_data.existing_code and input_data.modifications:
                # Modification mode
                logger.info(f"Modifying existing code for workflow {context.workflow_id}")
                generated_code = await self._modify_code(input_data, context)
                is_modification = True
                
                # Generate diff
                code_diff = self._generate_diff(input_data.existing_code, generated_code.html)
                
                # Validate that modifications don't break existing features
                validation_result = self._validate_modifications(
                    input_data.existing_code,
                    generated_code.html
                )
                if not validation_result["is_valid"]:
                    logger.warning(f"Modification validation warnings: {validation_result['warnings']}")
            else:
                # New generation mode
                logger.info(f"Generating new code for workflow {context.workflow_id}")
                generated_code = await self._generate_code(input_data, context)
            
            # Validate generated code
            framework = input_data.framework or requirements.get("framework", "vanilla")
            validation = self._validate_code(generated_code.html, framework)
            generated_code.validation = validation
            
            # Update metadata
            generated_code.metadata.has_tailwind = validation.has_tailwind_cdn
            generated_code.metadata.has_responsive_design = validation.has_responsive_patterns
            generated_code.metadata.has_meta_tags = (
                validation.has_title and 
                validation.has_description and 
                validation.has_viewport
            )
            
            # Calculate confidence score
            confidence = self._calculate_confidence(validation)
            
            logger.info(
                f"Code generation complete with confidence {confidence:.2f} "
                f"for workflow {context.workflow_id}"
            )
            
            output_data = {
                "html": generated_code.html,
                "metadata": generated_code.metadata.model_dump(),
                "validation": validation.model_dump(),
                "is_modification": is_modification,
            }
            
            if code_diff:
                output_data["code_diff"] = code_diff.model_dump()
            
            return CodeGenerationOutput(
                success=True,
                generated_code=generated_code,
                confidence=confidence,
                is_modification=is_modification,
                code_diff=code_diff,
                data=output_data
            )
            
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Code Generation Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Code generation failed: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _generate_code(
        self,
        input_data: CodeGenerationInput,
        context: AgentContext
    ) -> GeneratedCode:
        """Generate new code from requirements."""
        try:
            requirements = input_data.requirements
            framework = input_data.framework or requirements.get("framework", "vanilla")
            ui_library = input_data.ui_library or requirements.get("ui_library")
            
            # Route to framework-specific generation
            if framework.lower() == "react":
                return await self._generate_react_code(requirements, context, ui_library)
            elif framework.lower() == "vue":
                return await self._generate_vue_code(requirements, context, ui_library)
            elif framework.lower() == "nextjs" or framework.lower() == "next.js":
                return await self._generate_nextjs_code(requirements, context, ui_library)
            elif framework.lower() == "svelte":
                return await self._generate_svelte_code(requirements, context, ui_library)
            else:
                # Default to vanilla HTML
                return await self._generate_vanilla_code(requirements, input_data, context)
            
        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise AgentError(
                message=f"Failed to generate code: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _generate_vanilla_code(
        self,
        requirements: Dict[str, Any],
        input_data: CodeGenerationInput,
        context: AgentContext
    ) -> GeneratedCode:
        """Generate vanilla HTML/CSS/JS code."""
        site_type = requirements.get("site_type", "")
        
        # Try to use a template if available
        template = self.template_library.get_template(site_type)
        template_used = None
        
        if template and not input_data.template_preference:
            # Use template-based generation
            logger.info(f"Using template '{template.name}' for site type '{site_type}'")
            html_code = self._generate_from_template(template, requirements)
            template_used = template.name
        else:
            # Use LLM-based generation
            logger.info("Using LLM-based code generation")
            prompt = self._build_generation_prompt(requirements, input_data.template_preference)
            
            # Generate code using Gemini
            logger.info("Calling Gemini for code generation")
            html_code = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,  # Low temperature for consistency
                max_tokens=8000,
            )
            
            # Clean up the response (remove markdown code blocks if present)
            html_code = self._clean_code_response(html_code)
        
        # Ensure Tailwind CSS CDN is included
        html_code = self._ensure_tailwind_cdn(html_code)
        
        # Create metadata
        metadata = CodeMetadata(
            framework="vanilla",
            dependencies=["tailwindcss"],
            generated_at=datetime.utcnow(),
        )
        
        return GeneratedCode(
            html=html_code,
            metadata=metadata,
        )
    
    async def _generate_react_code(
        self,
        requirements: Dict[str, Any],
        context: AgentContext,
        ui_library: Optional[str] = None
    ) -> GeneratedCode:
        """Generate React code with component-based architecture."""
        try:
            logger.info(f"Generating React code with UI library: {ui_library or 'Tailwind CSS'}")
            
            # Research UI library dynamically if specified
            ui_lib_info = None
            if ui_library:
                ui_lib_info = await self._research_and_get_ui_library_info(ui_library, "react", context)
            
            # Build React-specific prompt
            prompt = self._build_react_prompt(requirements, ui_library, ui_lib_info)
            
            # Generate code using Gemini
            logger.info("Calling Gemini for React code generation")
            response = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=12000,
            )
            
            # Parse the response to extract multiple files
            files = self._parse_multi_file_response(response)
            
            # Ensure we have the required files
            if "index.html" not in files:
                files["index.html"] = self._generate_react_index_html()
            
            if "package.json" not in files:
                # Generate package.json with dynamic UI library packages
                npm_packages = ui_lib_info["npm_packages"] if ui_lib_info else {}
                files["package.json"] = self._generate_react_package_json(requirements, npm_packages)
            
            if "vite.config.js" not in files:
                files["vite.config.js"] = self._generate_react_vite_config()
            
            # Add UI library setup files if needed
            if ui_lib_info and ui_lib_info.get("setup_files"):
                files.update(ui_lib_info["setup_files"])
            
            # Main entry point
            main_file = files.get("src/main.jsx") or files.get("src/main.tsx") or files.get("src/App.jsx")
            
            # Build dependencies list
            dependencies = ["react", "react-dom", "vite"]
            if ui_lib_info:
                dependencies.extend(ui_lib_info["npm_packages"].keys())
            else:
                dependencies.append("tailwindcss")
            
            # Create metadata
            metadata = CodeMetadata(
                framework="react",
                dependencies=dependencies,
                generated_at=datetime.utcnow(),
                build_config={"buildCommand": "npm run build", "outputDir": "dist"}
            )
            
            return GeneratedCode(
                html=main_file or "",
                additional_files=files,
                metadata=metadata,
            )
            
        except Exception as e:
            logger.error(f"Error generating React code: {str(e)}")
            raise AgentError(
                message=f"Failed to generate React code: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def _build_react_prompt(
        self,
        requirements: Dict[str, Any],
        ui_library: Optional[str] = None,
        ui_lib_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for React code generation."""
        site_type = requirements.get("site_type", "website")
        pages = requirements.get("pages", [])
        color_palette = requirements.get("color_palette", "")
        key_features = requirements.get("key_features", [])
        design_style = requirements.get("design_style", "modern")
        target_audience = requirements.get("target_audience", "")
        content_tone = requirements.get("content_tone", "professional")
        
        # Get design style additions
        style_additions = self.design_style_library.get_style_prompt_addition(design_style)
        
        # Get UI library additions
        ui_library_additions = ""
        styling_instruction = "Use Tailwind utility classes for all styling"
        if ui_lib_info:
            ui_library_additions = ui_lib_info.get("prompt_addition", "")
            styling_instruction = f"Use {ui_library} components for all UI elements"
        
        prompt = f"""You are an expert React developer. Generate a complete React application based on the following requirements:

**Site Type:** {site_type}
**Design Style:** {design_style}
**Color Palette:** {color_palette or "Use a professional color scheme"}
**Target Audience:** {target_audience or "General audience"}
**Content Tone:** {content_tone}

**Pages to Include:**
{chr(10).join(f"- {page}" for page in pages) if pages else "- Single page application"}

**Key Features:**
{chr(10).join(f"- {feature}" for feature in key_features) if key_features else "- Basic informational content"}

**Requirements:**
1. Generate a complete React application using functional components and hooks
2. Use Vite as the build tool
3. Use Tailwind CSS for styling
4. Implement proper component structure with separation of concerns
5. Use useState and useContext for state management as needed
6. Add React Router for multi-page navigation if multiple pages are required
7. Include proper prop types and component documentation
8. Make the application fully responsive with mobile-first design
9. Add proper error boundaries
10. Include accessibility features (ARIA labels, semantic HTML)

**File Structure:**
Generate the following files:

1. **package.json** - Include React, React DOM, Vite, Tailwind CSS, and React Router (if needed)
2. **vite.config.js** - Vite configuration for React
3. **index.html** - HTML entry point with root div
4. **src/main.jsx** - Application entry point that renders the App component
5. **src/App.jsx** - Main App component with routing (if needed)
6. **src/components/** - Individual components as needed

**Code Guidelines:**
- Use modern React patterns (hooks, functional components)
- Implement proper state management with useState/useContext
- {styling_instruction}
- Add smooth transitions and hover effects
- Include loading states and error handling
- Write clean, maintainable code with comments
- Use realistic placeholder content
- Implement both dark mode and light mode support
- Ensure accessibility standards (WCAG) are maintained

{style_additions}

{ui_library_additions}

**Output Format:**
Return the code in the following format:

```filename: package.json
{{
  "name": "react-app",
  ...
}}
```

```filename: vite.config.js
import {{ defineConfig }} from 'vite'
...
```

```filename: index.html
<!DOCTYPE html>
...
```

```filename: src/main.jsx
import React from 'react'
...
```

```filename: src/App.jsx
import React from 'react'
...
```

Generate ALL necessary files. Make sure the code is production-ready and can be run immediately with `npm install && npm run dev`.
"""
        
        return prompt
    
    def _generate_react_index_html(self) -> str:
        """Generate default React index.html."""
        return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="React application" />
    <title>React App</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>"""
    
    def _generate_react_package_json(
        self,
        requirements: Dict[str, Any],
        npm_packages: Optional[Dict[str, str]] = None
    ) -> str:
        """Generate React package.json."""
        site_name = requirements.get("site_type", "react-app").lower().replace(" ", "-")
        has_routing = len(requirements.get("pages", [])) > 1
        
        package_json = {
            "name": site_name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.43",
                "@types/react-dom": "^18.2.17",
                "@vitejs/plugin-react": "^4.2.1",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.4.0",
                "vite": "^5.0.8"
            }
        }
        
        if has_routing:
            package_json["dependencies"]["react-router-dom"] = "^6.21.0"
        
        # Add dynamically researched npm packages
        if npm_packages:
            package_json["dependencies"].update(npm_packages)
        
        import json
        return json.dumps(package_json, indent=2)
    
    def _generate_react_vite_config(self) -> str:
        """Generate React vite.config.js."""
        return """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})"""
    
    async def _generate_vue_code(
        self,
        requirements: Dict[str, Any],
        context: AgentContext
    ) -> GeneratedCode:
        """Generate Vue code with single-file components."""
        try:
            logger.info("Generating Vue code")
            
            # Build Vue-specific prompt
            prompt = self._build_vue_prompt(requirements)
            
            # Generate code using Gemini
            logger.info("Calling Gemini for Vue code generation")
            response = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=12000,
            )
            
            # Parse the response to extract multiple files
            files = self._parse_multi_file_response(response)
            
            # Ensure we have the required files
            if "index.html" not in files:
                files["index.html"] = self._generate_vue_index_html()
            
            if "package.json" not in files:
                files["package.json"] = self._generate_vue_package_json(requirements)
            
            if "vite.config.js" not in files:
                files["vite.config.js"] = self._generate_vue_vite_config()
            
            # Main entry point
            main_file = files.get("src/main.js") or files.get("src/App.vue")
            
            # Create metadata
            metadata = CodeMetadata(
                framework="vue",
                dependencies=["vue", "vite", "tailwindcss"],
                generated_at=datetime.utcnow(),
                build_config={"buildCommand": "npm run build", "outputDir": "dist"}
            )
            
            return GeneratedCode(
                html=main_file or "",
                additional_files=files,
                metadata=metadata,
            )
            
        except Exception as e:
            logger.error(f"Error generating Vue code: {str(e)}")
            raise AgentError(
                message=f"Failed to generate Vue code: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def _build_vue_prompt(self, requirements: Dict[str, Any]) -> str:
        """Build prompt for Vue code generation."""
        site_type = requirements.get("site_type", "website")
        pages = requirements.get("pages", [])
        color_palette = requirements.get("color_palette", "")
        key_features = requirements.get("key_features", [])
        design_style = requirements.get("design_style", "modern")
        target_audience = requirements.get("target_audience", "")
        content_tone = requirements.get("content_tone", "professional")
        
        # Get design style additions
        style_additions = self.design_style_library.get_style_prompt_addition(design_style)
        
        prompt = f"""You are an expert Vue.js developer. Generate a complete Vue 3 application based on the following requirements:

**Site Type:** {site_type}
**Design Style:** {design_style}
**Color Palette:** {color_palette or "Use a professional color scheme"}
**Target Audience:** {target_audience or "General audience"}
**Content Tone:** {content_tone}

**Pages to Include:**
{chr(10).join(f"- {page}" for page in pages) if pages else "- Single page application"}

**Key Features:**
{chr(10).join(f"- {feature}" for feature in key_features) if key_features else "- Basic informational content"}

**Requirements:**
1. Generate a complete Vue 3 application using Composition API
2. Use Vite as the build tool
3. Use Tailwind CSS for styling
4. Create single-file components (.vue files) with proper structure
5. Use ref/reactive for state management
6. Add Vue Router for multi-page navigation if multiple pages are required
7. Use Pinia for global state management if needed
8. Include proper component props and emits
9. Make the application fully responsive with mobile-first design
10. Include accessibility features (ARIA labels, semantic HTML)

**File Structure:**
Generate the following files:

1. **package.json** - Include Vue 3, Vite, Tailwind CSS, and Vue Router (if needed)
2. **vite.config.js** - Vite configuration for Vue
3. **index.html** - HTML entry point with app div
4. **src/main.js** - Application entry point that creates and mounts the Vue app
5. **src/App.vue** - Main App component with router-view (if needed)
6. **src/components/** - Individual .vue components as needed

**Code Guidelines:**
- Use Composition API with <script setup> syntax
- Implement proper reactive state management with ref/reactive
- Use Tailwind utility classes for all styling
- Add smooth transitions with Vue's <Transition> component
- Include loading states and error handling
- Write clean, maintainable code with comments
- Use realistic placeholder content
- Follow Vue 3 best practices
- Implement both dark mode and light mode support
- Ensure accessibility standards (WCAG) are maintained

{style_additions}

**Output Format:**
Return the code in the following format:

```filename: package.json
{{
  "name": "vue-app",
  ...
}}
```

```filename: vite.config.js
import {{ defineConfig }} from 'vite'
...
```

```filename: index.html
<!DOCTYPE html>
...
```

```filename: src/main.js
import {{ createApp }} from 'vue'
...
```

```filename: src/App.vue
<template>
...
</template>

<script setup>
...
</script>

<style scoped>
...
</style>
```

Generate ALL necessary files. Make sure the code is production-ready and can be run immediately with `npm install && npm run dev`.
"""
        
        return prompt
    
    def _generate_vue_index_html(self) -> str:
        """Generate default Vue index.html."""
        return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Vue application" />
    <title>Vue App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>"""
    
    def _generate_vue_package_json(self, requirements: Dict[str, Any]) -> str:
        """Generate Vue package.json."""
        site_name = requirements.get("site_type", "vue-app").lower().replace(" ", "-")
        has_routing = len(requirements.get("pages", [])) > 1
        
        package_json = {
            "name": site_name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "vue": "^3.3.11"
            },
            "devDependencies": {
                "@vitejs/plugin-vue": "^5.0.0",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.4.0",
                "vite": "^5.0.8"
            }
        }
        
        if has_routing:
            package_json["dependencies"]["vue-router"] = "^4.2.5"
        
        import json
        return json.dumps(package_json, indent=2)
    
    def _generate_vue_vite_config(self) -> str:
        """Generate Vue vite.config.js."""
        return """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})"""
    
    async def _generate_nextjs_code(
        self,
        requirements: Dict[str, Any],
        context: AgentContext
    ) -> GeneratedCode:
        """Generate Next.js code with App Router."""
        try:
            logger.info("Generating Next.js code")
            
            # Build Next.js-specific prompt
            prompt = self._build_nextjs_prompt(requirements)
            
            # Generate code using Gemini
            logger.info("Calling Gemini for Next.js code generation")
            response = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=12000,
            )
            
            # Parse the response to extract multiple files
            files = self._parse_multi_file_response(response)
            
            # Ensure we have the required files
            if "package.json" not in files:
                files["package.json"] = self._generate_nextjs_package_json(requirements)
            
            if "next.config.js" not in files:
                files["next.config.js"] = self._generate_nextjs_config()
            
            # Main entry point
            main_file = files.get("app/page.js") or files.get("app/page.tsx") or files.get("app/layout.js")
            
            # Create metadata
            metadata = CodeMetadata(
                framework="nextjs",
                dependencies=["next", "react", "react-dom", "tailwindcss"],
                generated_at=datetime.utcnow(),
                build_config={"buildCommand": "next build", "outputDir": ".next"}
            )
            
            return GeneratedCode(
                html=main_file or "",
                additional_files=files,
                metadata=metadata,
            )
            
        except Exception as e:
            logger.error(f"Error generating Next.js code: {str(e)}")
            raise AgentError(
                message=f"Failed to generate Next.js code: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def _build_nextjs_prompt(self, requirements: Dict[str, Any]) -> str:
        """Build prompt for Next.js code generation."""
        site_type = requirements.get("site_type", "website")
        pages = requirements.get("pages", [])
        color_palette = requirements.get("color_palette", "")
        key_features = requirements.get("key_features", [])
        design_style = requirements.get("design_style", "modern")
        target_audience = requirements.get("target_audience", "")
        content_tone = requirements.get("content_tone", "professional")
        
        # Get design style additions
        style_additions = self.design_style_library.get_style_prompt_addition(design_style)
        
        prompt = f"""You are an expert Next.js developer. Generate a complete Next.js 14+ application using the App Router based on the following requirements:

**Site Type:** {site_type}
**Design Style:** {design_style}
**Color Palette:** {color_palette or "Use a professional color scheme"}
**Target Audience:** {target_audience or "General audience"}
**Content Tone:** {content_tone}

**Pages to Include:**
{chr(10).join(f"- {page}" for page in pages) if pages else "- Single page application"}

**Key Features:**
{chr(10).join(f"- {feature}" for feature in key_features) if key_features else "- Basic informational content"}

**Requirements:**
1. Generate a complete Next.js 14+ application using App Router (app/ directory)
2. Use Tailwind CSS for styling
3. Create proper layout.js/tsx and page.js/tsx files
4. Use Server Components by default, Client Components only when needed
5. Implement proper metadata with generateMetadata function for SEO
6. Add loading.js and error.js files for better UX
7. Create API routes in app/api/ if integrations are needed
8. Make the application fully responsive with mobile-first design
9. Include accessibility features (ARIA labels, semantic HTML)
10. Use Next.js Image component for optimized images

**File Structure:**
Generate the following files:

1. **package.json** - Include Next.js, React, Tailwind CSS
2. **next.config.js** - Next.js configuration
3. **app/layout.js** - Root layout with metadata and global styles
4. **app/page.js** - Home page component
5. **app/globals.css** - Global styles with Tailwind directives
6. **Additional pages** - Create page.js files in subdirectories for each page

**Code Guidelines:**
- Use Server Components by default for better performance
- Mark Client Components with 'use client' directive only when needed
- Implement proper metadata for SEO using generateMetadata
- Use Next.js Link component for navigation
- Use Next.js Image component for images
- Add smooth transitions and hover effects
- Include loading states with loading.js
- Write clean, maintainable code with comments
- Use realistic placeholder content
- Follow Next.js 14+ best practices
- Implement both dark mode and light mode support
- Ensure accessibility standards (WCAG) are maintained

{style_additions}

**Output Format:**
Return the code in the following format:

```filename: package.json
{{
  "name": "nextjs-app",
  ...
}}
```

```filename: next.config.js
/** @type {{import('next').NextConfig}} */
...
```

```filename: app/layout.js
import './globals.css'
...
```

```filename: app/page.js
export default function Home() {{
  ...
}}
```

```filename: app/globals.css
@tailwind base;
...
```

Generate ALL necessary files. Make sure the code is production-ready and can be run immediately with `npm install && npm run dev`.
"""
        
        return prompt
    
    def _generate_nextjs_package_json(self, requirements: Dict[str, Any]) -> str:
        """Generate Next.js package.json."""
        site_name = requirements.get("site_type", "nextjs-app").lower().replace(" ", "-")
        
        package_json = {
            "name": site_name,
            "version": "0.1.0",
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "^14.0.4",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.4.0",
                "eslint": "^8.56.0",
                "eslint-config-next": "^14.0.4"
            }
        }
        
        import json
        return json.dumps(package_json, indent=2)
    
    def _generate_nextjs_config(self) -> str:
        """Generate Next.js next.config.js."""
        return """/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['images.unsplash.com', 'via.placeholder.com'],
  },
}

module.exports = nextConfig"""
    
    async def _generate_svelte_code(
        self,
        requirements: Dict[str, Any],
        context: AgentContext
    ) -> GeneratedCode:
        """Generate Svelte code with reactive components."""
        try:
            logger.info("Generating Svelte code")
            
            # Build Svelte-specific prompt
            prompt = self._build_svelte_prompt(requirements)
            
            # Generate code using Gemini
            logger.info("Calling Gemini for Svelte code generation")
            response = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=12000,
            )
            
            # Parse the response to extract multiple files
            files = self._parse_multi_file_response(response)
            
            # Ensure we have the required files
            if "index.html" not in files:
                files["index.html"] = self._generate_svelte_index_html()
            
            if "package.json" not in files:
                files["package.json"] = self._generate_svelte_package_json(requirements)
            
            if "vite.config.js" not in files:
                files["vite.config.js"] = self._generate_svelte_vite_config()
            
            if "svelte.config.js" not in files:
                files["svelte.config.js"] = self._generate_svelte_config()
            
            # Main entry point
            main_file = files.get("src/main.js") or files.get("src/App.svelte")
            
            # Create metadata
            metadata = CodeMetadata(
                framework="svelte",
                dependencies=["svelte", "vite", "tailwindcss"],
                generated_at=datetime.utcnow(),
                build_config={"buildCommand": "npm run build", "outputDir": "dist"}
            )
            
            return GeneratedCode(
                html=main_file or "",
                additional_files=files,
                metadata=metadata,
            )
            
        except Exception as e:
            logger.error(f"Error generating Svelte code: {str(e)}")
            raise AgentError(
                message=f"Failed to generate Svelte code: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def _build_svelte_prompt(self, requirements: Dict[str, Any]) -> str:
        """Build prompt for Svelte code generation."""
        site_type = requirements.get("site_type", "website")
        pages = requirements.get("pages", [])
        color_palette = requirements.get("color_palette", "")
        key_features = requirements.get("key_features", [])
        design_style = requirements.get("design_style", "modern")
        target_audience = requirements.get("target_audience", "")
        content_tone = requirements.get("content_tone", "professional")
        
        # Get design style additions
        style_additions = self.design_style_library.get_style_prompt_addition(design_style)
        
        prompt = f"""You are an expert Svelte developer. Generate a complete Svelte application based on the following requirements:

**Site Type:** {site_type}
**Design Style:** {design_style}
**Color Palette:** {color_palette or "Use a professional color scheme"}
**Target Audience:** {target_audience or "General audience"}
**Content Tone:** {content_tone}

**Pages to Include:**
{chr(10).join(f"- {page}" for page in pages) if pages else "- Single page application"}

**Key Features:**
{chr(10).join(f"- {feature}" for feature in key_features) if key_features else "- Basic informational content"}

**Requirements:**
1. Generate a complete Svelte application with reactive components
2. Use Vite as the build tool
3. Use Tailwind CSS for styling
4. Create .svelte components with proper structure
5. Use Svelte stores for state management when needed
6. Add SvelteKit routing for multi-page navigation if multiple pages are required
7. Implement reactive statements with $: syntax
8. Include proper component props and events
9. Make the application fully responsive with mobile-first design
10. Include accessibility features (ARIA labels, semantic HTML)

**File Structure:**
Generate the following files:

1. **package.json** - Include Svelte, Vite, Tailwind CSS, and SvelteKit (if needed)
2. **vite.config.js** - Vite configuration for Svelte
3. **svelte.config.js** - Svelte configuration
4. **index.html** - HTML entry point with app div
5. **src/main.js** - Application entry point that creates the Svelte app
6. **src/App.svelte** - Main App component
7. **src/components/** - Individual .svelte components as needed
8. **src/stores/** - Svelte stores for state management if needed

**Code Guidelines:**
- Use reactive statements ($:) for computed values
- Implement proper state management with writable/readable stores
- Use Tailwind utility classes for all styling
- Add smooth transitions with Svelte's transition directives
- Include loading states and error handling
- Write clean, maintainable code with comments
- Use realistic placeholder content
- Follow Svelte best practices
- Use on:click and other event handlers properly
- Implement both dark mode and light mode support
- Ensure accessibility standards (WCAG) are maintained

{style_additions}

**Output Format:**
Return the code in the following format:

```filename: package.json
{{
  "name": "svelte-app",
  ...
}}
```

```filename: vite.config.js
import {{ defineConfig }} from 'vite'
...
```

```filename: svelte.config.js
import {{ vitePreprocess }} from '@sveltejs/vite-plugin-svelte'
...
```

```filename: index.html
<!DOCTYPE html>
...
```

```filename: src/main.js
import App from './App.svelte'
...
```

```filename: src/App.svelte
<script>
  // Component logic
</script>

<main>
  <!-- Template -->
</main>

<style>
  /* Component styles */
</style>
```

Generate ALL necessary files. Make sure the code is production-ready and can be run immediately with `npm install && npm run dev`.
"""
        
        return prompt
    
    def _generate_svelte_index_html(self) -> str:
        """Generate default Svelte index.html."""
        return """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Svelte application" />
    <title>Svelte App</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>"""
    
    def _generate_svelte_package_json(self, requirements: Dict[str, Any]) -> str:
        """Generate Svelte package.json."""
        site_name = requirements.get("site_type", "svelte-app").lower().replace(" ", "-")
        has_routing = len(requirements.get("pages", [])) > 1
        
        package_json = {
            "name": site_name,
            "private": True,
            "version": "0.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "svelte": "^4.2.8"
            },
            "devDependencies": {
                "@sveltejs/vite-plugin-svelte": "^3.0.1",
                "autoprefixer": "^10.4.16",
                "postcss": "^8.4.32",
                "svelte-preprocess": "^5.1.3",
                "tailwindcss": "^3.4.0",
                "vite": "^5.0.8"
            }
        }
        
        if has_routing:
            package_json["dependencies"]["@sveltejs/kit"] = "^2.0.0"
            package_json["dependencies"]["@sveltejs/adapter-auto"] = "^3.0.0"
        
        import json
        return json.dumps(package_json, indent=2)
    
    def _generate_svelte_vite_config(self) -> str:
        """Generate Svelte vite.config.js."""
        return """import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 3000,
    open: true
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})"""
    
    def _generate_svelte_config(self) -> str:
        """Generate Svelte svelte.config.js."""
        return """import { vitePreprocess } from '@sveltejs/vite-plugin-svelte'

export default {
  // Consult https://svelte.dev/docs#compile-time-svelte-preprocess
  // for more information about preprocessors
  preprocess: vitePreprocess(),
}"""
    
    async def _modify_code(
        self,
        input_data: CodeGenerationInput,
        context: AgentContext
    ) -> GeneratedCode:
        """Modify existing code based on requested changes."""
        try:
            existing_code = input_data.existing_code
            modifications = input_data.modifications
            requirements = input_data.requirements
            
            # Build prompt for code modification
            prompt = self._build_modification_prompt(
                existing_code,
                modifications,
                requirements
            )
            
            # Generate modified code using Gemini
            logger.info("Calling Gemini for code modification")
            html_code = await self.gemini.generate_text(
                prompt=prompt,
                temperature=0.2,
                max_tokens=8000,
            )
            
            # Clean up the response
            html_code = self._clean_code_response(html_code)
            
            # Ensure Tailwind CSS CDN is still included
            html_code = self._ensure_tailwind_cdn(html_code)
            
            # Create metadata
            metadata = CodeMetadata(
                framework="vanilla-html",
                dependencies=["tailwindcss"],
                generated_at=datetime.utcnow(),
            )
            
            return GeneratedCode(
                html=html_code,
                metadata=metadata,
            )
            
        except Exception as e:
            logger.error(f"Error modifying code: {str(e)}")
            raise AgentError(
                message=f"Failed to modify code: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    def _generate_from_template(
        self,
        template: SiteTemplate,
        requirements: Dict[str, Any]
    ) -> str:
        """Generate code from a template with customizations."""
        # Extract customization values from requirements
        customizations = {
            "site_title": requirements.get("site_type", "My Site").title(),
            "description": f"A {requirements.get('site_type', 'website')} showcasing {', '.join(requirements.get('key_features', [])[:3])}",
            "name": "Your Name",
            "company_name": "Your Company",
        }
        
        # Add color scheme
        color_palette = requirements.get("color_palette", "")
        if "blue" in color_palette.lower():
            customizations["accent_color"] = "blue-600"
            customizations["secondary_color"] = "blue-500"
        elif "purple" in color_palette.lower() or "violet" in color_palette.lower():
            customizations["accent_color"] = "purple-600"
            customizations["secondary_color"] = "purple-500"
        elif "green" in color_palette.lower():
            customizations["accent_color"] = "green-600"
            customizations["secondary_color"] = "green-500"
        elif "red" in color_palette.lower():
            customizations["accent_color"] = "red-600"
            customizations["secondary_color"] = "red-500"
        else:
            customizations["accent_color"] = "indigo-600"
            customizations["secondary_color"] = "indigo-500"
        
        # Add design style specific customizations
        design_style = requirements.get("design_style", "")
        if "dark" in design_style.lower():
            customizations["bg_color"] = "gray-900"
            customizations["text_color"] = "gray-100"
        else:
            customizations["bg_color"] = "gray-50"
            customizations["text_color"] = "gray-900"
        
        # Customize template
        html_code = self.template_library.customize_template(template, customizations)
        
        return html_code
    
    def _build_generation_prompt(
        self,
        requirements: Dict[str, Any],
        template_preference: Optional[str] = None
    ) -> str:
        """Build prompt for generating new code."""
        site_type = requirements.get("site_type", "website")
        pages = requirements.get("pages", [])
        color_palette = requirements.get("color_palette", "")
        key_features = requirements.get("key_features", [])
        design_style = requirements.get("design_style", "modern")
        target_audience = requirements.get("target_audience", "")
        content_tone = requirements.get("content_tone", "professional")
        
        # Get design style additions
        style_additions = self.design_style_library.get_style_prompt_addition(design_style)
        
        prompt = f"""You are an expert web developer. Generate a complete, production-ready HTML website based on the following requirements:

**Site Type:** {site_type}
**Design Style:** {design_style}
**Color Palette:** {color_palette or "Use a professional color scheme"}
**Target Audience:** {target_audience or "General audience"}
**Content Tone:** {content_tone}

**Pages to Include:**
{chr(10).join(f"- {page}" for page in pages) if pages else "- Single page site"}

**Key Features:**
{chr(10).join(f"- {feature}" for feature in key_features) if key_features else "- Basic informational content"}

**Requirements:**
1. Generate a SINGLE, complete HTML file with embedded CSS and JavaScript
2. Use Tailwind CSS via CDN for styling (include the CDN link in the <head>)
3. Make the site fully responsive with mobile-first design
4. Include proper semantic HTML5 structure
5. Add comprehensive SEO meta tags (title, description, viewport, Open Graph)
6. Use modern, clean design with good UX
7. Include ARIA labels for accessibility
8. Add smooth scrolling and subtle animations
9. Ensure all images have alt text
10. Use placeholder images from https://images.unsplash.com/ or https://via.placeholder.com/

**Structure Guidelines:**
- Use semantic HTML5 tags (header, nav, main, section, article, footer)
- Implement a responsive navigation menu
- Create visually appealing sections with proper spacing
- Use Tailwind utility classes for all styling
- Add hover effects and transitions
- Include a footer with relevant links

**Content Guidelines:**
- Use realistic placeholder content that matches the site type
- Write engaging, {content_tone} copy
- Include clear calls-to-action
- Add relevant icons (use Unicode symbols or Heroicons via CDN)
- Implement both dark mode and light mode support
- Ensure accessibility standards (WCAG) are maintained

{style_additions}

Generate ONLY the HTML code, no explanations. The code should be ready to deploy immediately.
"""
        
        return prompt
    
    def _build_modification_prompt(
        self,
        existing_code: str,
        modifications: List[str],
        requirements: Dict[str, Any]
    ) -> str:
        """Build prompt for modifying existing code."""
        prompt = f"""You are an expert web developer. Modify the existing HTML code based on the requested changes.

**Existing Code:**
```html
{existing_code}
```

**Requested Modifications:**
{chr(10).join(f"{i+1}. {mod}" for i, mod in enumerate(modifications))}

**Original Requirements (for context):**
{requirements}

**Requirements:**
1. Make ONLY the requested modifications
2. Preserve all existing functionality that isn't being changed
3. Maintain the same structure and style unless specifically requested to change
4. Ensure the modified code is still valid HTML
5. Keep Tailwind CSS CDN link
6. Maintain responsive design
7. Preserve all meta tags and SEO elements
8. Ensure accessibility features remain intact

Generate the COMPLETE modified HTML code, no explanations. The code should be ready to deploy immediately.
"""
        
        return prompt
    
    def _parse_multi_file_response(self, response: str) -> Dict[str, str]:
        """
        Parse LLM response containing multiple files.
        
        Expected format:
        ```filename: path/to/file.ext
        file content here
        ```
        
        Returns:
            Dictionary mapping file paths to content
        """
        files = {}
        
        # Split by code blocks
        import re
        
        # Pattern to match: ```filename: path/to/file.ext
        pattern = r'```filename:\s*([^\n]+)\n(.*?)```'
        matches = re.findall(pattern, response, re.DOTALL)
        
        for filename, content in matches:
            filename = filename.strip()
            content = content.strip()
            files[filename] = content
        
        # If no files found with filename pattern, try standard code blocks
        if not files:
            # Try to extract files based on common patterns
            if "package.json" in response:
                json_match = re.search(r'```(?:json)?\n(\{[\s\S]*?"name"[\s\S]*?\})\n```', response)
                if json_match:
                    files["package.json"] = json_match.group(1).strip()
            
            if "vite.config" in response:
                vite_match = re.search(r'```(?:javascript|js)?\n(import.*?vite.*?export default[\s\S]*?)\n```', response)
                if vite_match:
                    files["vite.config.js"] = vite_match.group(1).strip()
            
            if "index.html" in response:
                html_match = re.search(r'```(?:html)?\n(<!DOCTYPE html>[\s\S]*?</html>)\n```', response)
                if html_match:
                    files["index.html"] = html_match.group(1).strip()
            
            # Try to find main.jsx or App.jsx
            jsx_matches = re.findall(r'```(?:jsx|javascript)?\n(import React[\s\S]*?)\n```', response)
            if jsx_matches:
                # First one is likely main.jsx, second is App.jsx
                if len(jsx_matches) >= 1:
                    files["src/main.jsx"] = jsx_matches[0].strip()
                if len(jsx_matches) >= 2:
                    files["src/App.jsx"] = jsx_matches[1].strip()
        
        return files
    
    def _clean_code_response(self, response: str) -> str:
        """Clean up LLM response to extract pure HTML."""
        # Remove markdown code blocks
        response = response.strip()
        
        # Remove ```html or ``` markers
        if response.startswith("```html"):
            response = response[7:]
        elif response.startswith("```"):
            response = response[3:]
        
        if response.endswith("```"):
            response = response[:-3]
        
        response = response.strip()
        
        # Ensure it starts with <!DOCTYPE html> or <html>
        if not response.lower().startswith("<!doctype") and not response.lower().startswith("<html"):
            # Try to find the start of HTML
            html_start = response.lower().find("<!doctype")
            if html_start == -1:
                html_start = response.lower().find("<html")
            
            if html_start > 0:
                response = response[html_start:]
        
        return response
    
    def _ensure_tailwind_cdn(self, html_code: str) -> str:
        """Ensure Tailwind CSS CDN is included in the HTML."""
        tailwind_cdn = '<script src="https://cdn.tailwindcss.com"></script>'
        
        # Check if Tailwind is already included
        if "cdn.tailwindcss.com" in html_code or "tailwindcss" in html_code.lower():
            return html_code
        
        # Try to inject before </head>
        if "</head>" in html_code:
            html_code = html_code.replace("</head>", f"  {tailwind_cdn}\n</head>")
        else:
            # If no </head>, try to add after <head>
            if "<head>" in html_code:
                html_code = html_code.replace("<head>", f"<head>\n  {tailwind_cdn}")
            else:
                # Last resort: add at the beginning
                html_code = tailwind_cdn + "\n" + html_code
        
        return html_code
    
    def _validate_code(self, html_code: str, framework: str = "vanilla") -> CodeValidation:
        """Validate generated code based on framework."""
        if framework == "react":
            return self._validate_react_code(html_code)
        elif framework == "vue":
            return self._validate_vue_code(html_code)
        elif framework == "nextjs":
            return self._validate_nextjs_code(html_code)
        elif framework == "svelte":
            return self._validate_svelte_code(html_code)
        else:
            return self._validate_vanilla_code(html_code)
    
    def _validate_vanilla_code(self, html_code: str) -> CodeValidation:
        """Validate generated HTML code."""
        validation = CodeValidation()
        
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_code, 'html.parser')
            
            # Check for valid HTML structure
            if not soup.find('html'):
                validation.is_valid_html = False
                validation.validation_errors.append("Missing <html> tag")
            
            # Check for meta tags
            title_tag = soup.find('title')
            validation.has_title = title_tag is not None
            if not validation.has_title:
                validation.validation_warnings.append("Missing <title> tag")
            
            # Check for description meta tag
            description_meta = soup.find('meta', attrs={'name': 'description'})
            validation.has_description = description_meta is not None
            if not validation.has_description:
                validation.validation_warnings.append("Missing description meta tag")
            
            # Check for viewport meta tag
            viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
            validation.has_viewport = viewport_meta is not None
            if not validation.has_viewport:
                validation.validation_warnings.append("Missing viewport meta tag")
            
            # Check for Tailwind CSS CDN
            tailwind_script = soup.find('script', src=re.compile(r'tailwindcss'))
            validation.has_tailwind_cdn = tailwind_script is not None
            if not validation.has_tailwind_cdn:
                validation.validation_warnings.append("Tailwind CSS CDN not found")
            
            # Check for responsive design patterns
            # Look for common responsive classes or media queries
            html_str = str(soup)
            responsive_indicators = [
                'sm:', 'md:', 'lg:', 'xl:', '2xl:',  # Tailwind breakpoints
                '@media',  # CSS media queries
                'flex', 'grid',  # Responsive layout systems
            ]
            validation.has_responsive_patterns = any(
                indicator in html_str for indicator in responsive_indicators
            )
            if not validation.has_responsive_patterns:
                validation.validation_warnings.append("No responsive design patterns detected")
            
            # Calculate confidence score
            validation.confidence_score = self._calculate_validation_confidence(validation)
            
        except Exception as e:
            logger.error(f"Error validating HTML: {str(e)}")
            validation.is_valid_html = False
            validation.validation_errors.append(f"HTML parsing error: {str(e)}")
            validation.confidence_score = 0.0
        
        return validation
    
    def _validate_react_code(self, code: str) -> CodeValidation:
        """Validate React code."""
        validation = CodeValidation()
        validation.is_valid_html = True  # React doesn't use HTML directly
        
        try:
            # Check for React imports
            if "import React" not in code and "import" in code:
                validation.validation_warnings.append("React import may be missing")
            
            # Check for hooks usage
            if "useState" in code or "useEffect" in code or "useContext" in code:
                validation.has_responsive_patterns = True
            
            # Check for proper component structure
            if "function" in code or "const" in code and "=>" in code:
                validation.has_title = True  # Using this field for component structure
            
            # Check for JSX syntax
            if "return (" in code or "return <" in code:
                validation.has_description = True  # Using this field for JSX presence
            
            # Check for Tailwind classes
            if "className=" in code:
                validation.has_tailwind_cdn = True
            
            # Check for key props in lists
            if ".map(" in code and "key=" not in code:
                validation.validation_warnings.append("Missing key props in list rendering")
            
            # Calculate confidence
            validation.confidence_score = self._calculate_validation_confidence(validation)
            
        except Exception as e:
            logger.error(f"Error validating React code: {str(e)}")
            validation.validation_errors.append(f"Validation error: {str(e)}")
        
        return validation
    
    def _validate_vue_code(self, code: str) -> CodeValidation:
        """Validate Vue code."""
        validation = CodeValidation()
        validation.is_valid_html = True  # Vue uses SFC format
        
        try:
            # Check for Vue SFC structure
            if "<template>" in code and "<script" in code:
                validation.has_title = True  # Using this field for SFC structure
            else:
                validation.validation_warnings.append("Missing proper Vue SFC structure")
            
            # Check for Composition API
            if "setup" in code or "ref" in code or "reactive" in code:
                validation.has_responsive_patterns = True
            
            # Check for Tailwind classes
            if "class=" in code:
                validation.has_tailwind_cdn = True
            
            # Check for v-for with key
            if "v-for=" in code and ":key=" not in code:
                validation.validation_warnings.append("Missing :key binding in v-for")
            
            # Check for proper imports
            if "import" in code:
                validation.has_description = True  # Using this field for imports
            
            # Calculate confidence
            validation.confidence_score = self._calculate_validation_confidence(validation)
            
        except Exception as e:
            logger.error(f"Error validating Vue code: {str(e)}")
            validation.validation_errors.append(f"Validation error: {str(e)}")
        
        return validation
    
    def _validate_nextjs_code(self, code: str) -> CodeValidation:
        """Validate Next.js code."""
        validation = CodeValidation()
        validation.is_valid_html = True  # Next.js uses JSX
        
        try:
            # Check for proper Next.js structure
            if "export default" in code:
                validation.has_title = True  # Using this field for export structure
            
            # Check for metadata (Next.js 14+)
            if "metadata" in code or "generateMetadata" in code:
                validation.has_description = True  # Using this field for metadata
                validation.has_viewport = True
            else:
                validation.validation_warnings.append("Missing metadata for SEO")
            
            # Check for Server/Client components
            if "'use client'" in code or '"use client"' in code:
                # Client component - should have interactivity
                if "useState" not in code and "useEffect" not in code:
                    validation.validation_warnings.append("Client component without hooks")
            
            # Check for Tailwind classes
            if "className=" in code:
                validation.has_tailwind_cdn = True
            
            # Check for Next.js Image component
            if "<img" in code and "next/image" not in code:
                validation.validation_warnings.append("Consider using next/image for optimization")
            
            # Check for responsive patterns
            if "md:" in code or "lg:" in code:
                validation.has_responsive_patterns = True
            
            # Calculate confidence
            validation.confidence_score = self._calculate_validation_confidence(validation)
            
        except Exception as e:
            logger.error(f"Error validating Next.js code: {str(e)}")
            validation.validation_errors.append(f"Validation error: {str(e)}")
        
        return validation
    
    def _validate_svelte_code(self, code: str) -> CodeValidation:
        """Validate Svelte code."""
        validation = CodeValidation()
        validation.is_valid_html = True  # Svelte uses SFC format
        
        try:
            # Check for Svelte component structure
            if "<script>" in code or "<script " in code:
                validation.has_title = True  # Using this field for component structure
            
            # Check for reactive statements
            if "$:" in code:
                validation.has_responsive_patterns = True
            
            # Check for Tailwind classes
            if "class=" in code:
                validation.has_tailwind_cdn = True
            
            # Check for proper event handlers
            if "on:" in code:
                validation.has_description = True  # Using this field for event handlers
            
            # Check for each blocks with key
            if "{#each" in code and "(" not in code:
                validation.validation_warnings.append("Consider using keyed each blocks")
            
            # Check for stores
            if "$" in code and "writable" in code or "readable" in code:
                validation.has_viewport = True  # Using this field for stores
            
            # Calculate confidence
            validation.confidence_score = self._calculate_validation_confidence(validation)
            
        except Exception as e:
            logger.error(f"Error validating Svelte code: {str(e)}")
            validation.validation_errors.append(f"Validation error: {str(e)}")
        
        return validation
    
    def _calculate_validation_confidence(self, validation: CodeValidation) -> float:
        """Calculate confidence score based on validation results."""
        score = 0.0
        max_score = 6.0
        
        # Valid HTML structure (most important)
        if validation.is_valid_html:
            score += 2.0
        
        # Meta tags
        if validation.has_title:
            score += 1.0
        if validation.has_description:
            score += 0.5
        if validation.has_viewport:
            score += 0.5
        
        # Tailwind CSS
        if validation.has_tailwind_cdn:
            score += 1.0
        
        # Responsive design
        if validation.has_responsive_patterns:
            score += 1.0
        
        return score / max_score
    
    def _calculate_confidence(self, validation: CodeValidation) -> float:
        """Calculate overall confidence score for generated code."""
        # Use validation confidence as base
        confidence = validation.confidence_score
        
        # Reduce confidence for errors
        if validation.validation_errors:
            confidence *= 0.5
        
        # Slightly reduce for warnings
        if validation.validation_warnings:
            confidence *= 0.9
        
        return max(0.0, min(1.0, confidence))
    
    def _generate_diff(self, old_code: str, new_code: str) -> CodeDiff:
        """
        Generate diff between old and new code.
        
        Args:
            old_code: Original code
            new_code: Modified code
            
        Returns:
            CodeDiff with diff information
        """
        try:
            old_lines = old_code.splitlines(keepends=True)
            new_lines = new_code.splitlines(keepends=True)
            
            # Generate unified diff
            diff = list(difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile='original',
                tofile='modified',
                lineterm=''
            ))
            
            # Count changes
            added_lines = sum(1 for line in diff if line.startswith('+') and not line.startswith('+++'))
            removed_lines = sum(1 for line in diff if line.startswith('-') and not line.startswith('---'))
            
            # Extract modified sections (context around changes)
            modified_sections = []
            current_section = []
            in_change = False
            
            for line in diff:
                if line.startswith('@@'):
                    if current_section:
                        modified_sections.append(''.join(current_section))
                        current_section = []
                    in_change = True
                    current_section.append(line + '\n')
                elif in_change:
                    current_section.append(line + '\n')
                    if len(current_section) > 10:  # Limit section size
                        modified_sections.append(''.join(current_section))
                        current_section = []
                        in_change = False
            
            if current_section:
                modified_sections.append(''.join(current_section))
            
            # Generate summary
            diff_summary = f"Modified {added_lines + removed_lines} lines ({added_lines} added, {removed_lines} removed)"
            
            return CodeDiff(
                added_lines=added_lines,
                removed_lines=removed_lines,
                modified_sections=modified_sections[:5],  # Limit to 5 sections
                diff_summary=diff_summary
            )
            
        except Exception as e:
            logger.error(f"Error generating diff: {str(e)}")
            return CodeDiff(
                diff_summary="Unable to generate diff"
            )
    
    def _validate_modifications(
        self,
        old_code: str,
        new_code: str
    ) -> Dict[str, Any]:
        """
        Validate that modifications don't break existing features.
        
        Args:
            old_code: Original code
            new_code: Modified code
            
        Returns:
            Dictionary with validation results
        """
        warnings = []
        is_valid = True
        
        try:
            # Parse both versions
            old_soup = BeautifulSoup(old_code, 'html.parser')
            new_soup = BeautifulSoup(new_code, 'html.parser')
            
            # Check that essential elements are preserved
            # 1. Check for DOCTYPE
            if '<!DOCTYPE' in old_code and '<!DOCTYPE' not in new_code:
                warnings.append("DOCTYPE declaration was removed")
            
            # 2. Check for meta tags
            old_metas = old_soup.find_all('meta')
            new_metas = new_soup.find_all('meta')
            if len(old_metas) > len(new_metas):
                warnings.append(f"Some meta tags were removed ({len(old_metas)} -> {len(new_metas)})")
            
            # 3. Check for Tailwind CSS
            if 'tailwindcss' in old_code and 'tailwindcss' not in new_code:
                warnings.append("Tailwind CSS CDN was removed")
            
            # 4. Check for major structural elements
            old_sections = len(old_soup.find_all(['section', 'article', 'div']))
            new_sections = len(new_soup.find_all(['section', 'article', 'div']))
            if new_sections < old_sections * 0.5:  # More than 50% reduction
                warnings.append("Significant structural elements were removed")
            
            # 5. Check for navigation
            old_nav = old_soup.find('nav')
            new_nav = new_soup.find('nav')
            if old_nav and not new_nav:
                warnings.append("Navigation element was removed")
            
            # 6. Check for forms
            old_forms = old_soup.find_all('form')
            new_forms = new_soup.find_all('form')
            if len(old_forms) > len(new_forms):
                warnings.append(f"Some forms were removed ({len(old_forms)} -> {len(new_forms)})")
            
        except Exception as e:
            logger.error(f"Error validating modifications: {str(e)}")
            warnings.append(f"Validation error: {str(e)}")
        
        return {
            "is_valid": is_valid,
            "warnings": warnings
        }
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate Code Generation Agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Operation failed")
            return result
        
        if not isinstance(output, CodeGenerationOutput):
            result.add_error("Invalid output type")
            return result
        
        if not output.generated_code:
            result.add_error("No generated code in output")
            return result
        
        generated_code = output.generated_code
        
        # Check if HTML is present
        if not generated_code.html or len(generated_code.html.strip()) == 0:
            result.add_error("Generated HTML is empty")
            return result
        
        # Check validation results
        if generated_code.validation:
            val = generated_code.validation
            
            if not val.is_valid_html:
                result.add_error("Generated HTML is not valid")
            
            if val.validation_errors:
                for error in val.validation_errors:
                    result.add_error(f"Validation error: {error}")
            
            if val.validation_warnings:
                for warning in val.validation_warnings:
                    result.add_warning(f"Validation warning: {warning}")
            
            # Set confidence from validation
            result.confidence = val.confidence_score
        
        return result
