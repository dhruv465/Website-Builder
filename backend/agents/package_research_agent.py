"""
Package Research Agent for dynamically learning about npm packages.

This agent can research any npm package the user mentions and learn:
- How to install it
- How to import and use it
- Configuration requirements
- Best practices
- Example code
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from services.gemini_service import gemini_service
from utils.logging import logger


class PackageResearchInput(AgentInput):
    """Input for package research."""
    package_name: str = Field(..., description="Name of the npm package to research")
    framework: str = Field(..., description="Framework context (react, vue, nextjs, svelte)")
    use_case: Optional[str] = Field(None, description="What the user wants to use it for")


class PackageInfo(BaseModel):
    """Information about an npm package."""
    package_name: str
    version: str = "latest"
    description: str
    installation_command: str
    peer_dependencies: List[str] = Field(default_factory=list)
    import_examples: List[str] = Field(default_factory=list)
    usage_examples: List[str] = Field(default_factory=list)
    configuration_required: bool = False
    configuration_steps: List[str] = Field(default_factory=list)
    setup_files: Dict[str, str] = Field(default_factory=dict)
    best_practices: List[str] = Field(default_factory=list)
    common_pitfalls: List[str] = Field(default_factory=list)
    compatible_with_framework: bool = True
    alternative_packages: List[str] = Field(default_factory=list)


class PackageResearchOutput(AgentOutput):
    """Output for package research."""
    package_info: Optional[PackageInfo] = None
    research_summary: str = ""
    can_be_used: bool = True
    warnings: List[str] = Field(default_factory=list)


class PackageResearchAgent(BaseAgent):
    """
    Package Research Agent for learning about npm packages dynamically.
    
    This agent uses the LLM to research any npm package and understand:
    - Installation requirements
    - Usage patterns
    - Configuration needs
    - Best practices
    """
    
    def __init__(self):
        """Initialize Package Research Agent."""
        super().__init__(name="PackageResearchAgent")
        self.gemini = gemini_service
        logger.info("Package Research Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute package research.
        
        Args:
            input_data: Input data with package name and framework
            context: Execution context
            
        Returns:
            PackageResearchOutput with package information
        """
        try:
            if not isinstance(input_data, PackageResearchInput):
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            logger.info(f"Researching package: {input_data.package_name} for {input_data.framework}")
            
            # Research the package using LLM
            package_info = await self._research_package(
                input_data.package_name,
                input_data.framework,
                input_data.use_case
            )
            
            # Generate research summary
            summary = self._generate_summary(package_info)
            
            # Check for warnings
            warnings = self._check_warnings(package_info, input_data.framework)
            
            return PackageResearchOutput(
                success=True,
                package_info=package_info,
                research_summary=summary,
                can_be_used=package_info.compatible_with_framework,
                warnings=warnings,
                confidence=0.9 if package_info.compatible_with_framework else 0.5,
                data={
                    "package_name": package_info.package_name,
                    "version": package_info.version,
                    "installation": package_info.installation_command,
                }
            )
            
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Package Research Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Package research failed: {str(e)}",
                error_type=ErrorType.LLM_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=True,
            )
    
    async def _research_package(
        self,
        package_name: str,
        framework: str,
        use_case: Optional[str] = None
    ) -> PackageInfo:
        """Research a package using LLM."""
        prompt = self._build_research_prompt(package_name, framework, use_case)
        
        logger.info(f"Calling Gemini to research {package_name}")
        response = await self.gemini.generate_text(
            prompt=prompt,
            temperature=0.1,  # Low temperature for factual information
            max_tokens=4000,
        )
        
        # Parse the LLM response into structured data
        package_info = self._parse_research_response(response, package_name, framework)
        
        return package_info
    
    def _build_research_prompt(
        self,
        package_name: str,
        framework: str,
        use_case: Optional[str] = None
    ) -> str:
        """Build prompt for package research."""
        use_case_text = f"\n**Use Case:** {use_case}" if use_case else ""
        
        prompt = f"""You are an expert in npm packages and {framework} development. Research the npm package "{package_name}" and provide comprehensive information.

**Package:** {package_name}
**Framework:** {framework}{use_case_text}

Please provide the following information in a structured format:

1. **PACKAGE_NAME**: The exact npm package name
2. **VERSION**: Latest stable version (or "latest")
3. **DESCRIPTION**: Brief description of what the package does
4. **INSTALLATION**: Exact npm install command
5. **PEER_DEPENDENCIES**: List any peer dependencies required (comma-separated)
6. **COMPATIBLE**: Is this package compatible with {framework}? (YES/NO)
7. **IMPORT_EXAMPLES**: 3-5 common import statements (one per line)
8. **USAGE_EXAMPLES**: 3-5 code examples showing how to use it (one per line)
9. **CONFIGURATION_REQUIRED**: Does it need configuration? (YES/NO)
10. **CONFIGURATION_STEPS**: If yes, list configuration steps (one per line)
11. **SETUP_FILES**: Any setup files needed (format: filename: content)
12. **BEST_PRACTICES**: 3-5 best practices (one per line)
13. **COMMON_PITFALLS**: 3-5 common mistakes to avoid (one per line)
14. **ALTERNATIVES**: Alternative packages that do similar things (comma-separated)

**IMPORTANT RULES:**
- Provide ACCURATE, up-to-date information
- If the package doesn't exist, say "PACKAGE_NOT_FOUND"
- If incompatible with {framework}, explain why
- Use actual code examples, not placeholders
- Be specific about versions and commands

Format your response EXACTLY like this:

```
PACKAGE_NAME: package-name
VERSION: 1.2.3
DESCRIPTION: What it does
INSTALLATION: npm install package-name
PEER_DEPENDENCIES: react, react-dom
COMPATIBLE: YES
IMPORT_EXAMPLES:
- import {{ Component }} from 'package-name'
- import {{ useHook }} from 'package-name/hooks'
USAGE_EXAMPLES:
- <Component prop="value" />
- const data = useHook()
CONFIGURATION_REQUIRED: YES
CONFIGURATION_STEPS:
- Add to vite.config.js
- Create config file
SETUP_FILES:
config.js: export default {{ ... }}
BEST_PRACTICES:
- Always use TypeScript
- Memoize expensive operations
COMMON_PITFALLS:
- Forgetting to import CSS
- Not handling errors
ALTERNATIVES: alternative-package-1, alternative-package-2
```

Provide the research now:
"""
        return prompt
    
    def _parse_research_response(
        self,
        response: str,
        package_name: str,
        framework: str
    ) -> PackageInfo:
        """Parse LLM research response into PackageInfo."""
        # Check if package was not found
        if "PACKAGE_NOT_FOUND" in response:
            logger.warning(f"Package {package_name} not found")
            return PackageInfo(
                package_name=package_name,
                description=f"Package '{package_name}' not found in npm registry",
                installation_command=f"npm install {package_name}",
                compatible_with_framework=False,
                warnings=[f"Package '{package_name}' may not exist or is not well-documented"]
            )
        
        # Parse structured response
        lines = response.strip().split('\n')
        data = {}
        current_key = None
        current_list = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('```'):
                continue
            
            if ':' in line and not line.startswith('-'):
                # New key-value pair
                if current_key and current_list:
                    data[current_key] = current_list
                    current_list = []
                
                key, value = line.split(':', 1)
                key = key.strip().upper().replace(' ', '_')
                value = value.strip()
                
                if key in ['IMPORT_EXAMPLES', 'USAGE_EXAMPLES', 'CONFIGURATION_STEPS', 'BEST_PRACTICES', 'COMMON_PITFALLS']:
                    current_key = key
                    if value:
                        current_list.append(value)
                else:
                    data[key] = value
                    current_key = None
            elif line.startswith('-') and current_key:
                # List item
                current_list.append(line[1:].strip())
        
        # Add last list
        if current_key and current_list:
            data[current_key] = current_list
        
        # Build PackageInfo
        return PackageInfo(
            package_name=data.get('PACKAGE_NAME', package_name),
            version=data.get('VERSION', 'latest'),
            description=data.get('DESCRIPTION', ''),
            installation_command=data.get('INSTALLATION', f'npm install {package_name}'),
            peer_dependencies=data.get('PEER_DEPENDENCIES', '').split(',') if data.get('PEER_DEPENDENCIES') else [],
            import_examples=data.get('IMPORT_EXAMPLES', []),
            usage_examples=data.get('USAGE_EXAMPLES', []),
            configuration_required=data.get('CONFIGURATION_REQUIRED', 'NO').upper() == 'YES',
            configuration_steps=data.get('CONFIGURATION_STEPS', []),
            best_practices=data.get('BEST_PRACTICES', []),
            common_pitfalls=data.get('COMMON_PITFALLS', []),
            compatible_with_framework=data.get('COMPATIBLE', 'YES').upper() == 'YES',
            alternative_packages=data.get('ALTERNATIVES', '').split(',') if data.get('ALTERNATIVES') else []
        )
    
    def _generate_summary(self, package_info: PackageInfo) -> str:
        """Generate a human-readable summary."""
        summary = f"Package: {package_info.package_name}\n"
        summary += f"Description: {package_info.description}\n"
        summary += f"Installation: {package_info.installation_command}\n"
        
        if package_info.peer_dependencies:
            summary += f"Peer Dependencies: {', '.join(package_info.peer_dependencies)}\n"
        
        if package_info.configuration_required:
            summary += "Configuration: Required\n"
        
        return summary
    
    def _check_warnings(self, package_info: PackageInfo, framework: str) -> List[str]:
        """Check for potential warnings."""
        warnings = []
        
        if not package_info.compatible_with_framework:
            warnings.append(f"Package may not be fully compatible with {framework}")
        
        if package_info.configuration_required:
            warnings.append("This package requires additional configuration")
        
        if package_info.peer_dependencies:
            warnings.append(f"Requires peer dependencies: {', '.join(package_info.peer_dependencies)}")
        
        return warnings
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """Validate Package Research Agent output."""
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Research failed")
            return result
        
        if not isinstance(output, PackageResearchOutput):
            result.add_error("Invalid output type")
            return result
        
        if not output.package_info:
            result.add_error("No package information in output")
            return result
        
        return result


# Global instance
package_research_agent = PackageResearchAgent()
