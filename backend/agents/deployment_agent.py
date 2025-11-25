"""
Deployment Agent for deploying websites to Vercel.

This agent:
- Validates HTML before deployment
- Creates or updates Vercel projects
- Deploys sites to Vercel
- Verifies deployment health
- Stores deployment records in database
- Generates unique site names
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup
import re
import uuid
import asyncio

from agents.base_agent import (
    BaseAgent,
    AgentInput,
    AgentOutput,
    AgentContext,
    ValidationResult,
    AgentError,
    ErrorType,
)
from agents.framework_configs import (
    Framework,
    get_framework_config,
    get_vercel_project_settings,
    get_vercel_config_json,
    validate_framework_files,
)
from services.vercel_client import vercel_client, VercelDeployment as VercelDeploymentModel
from services.retry_handler import retry_with_backoff, RetryConfig
from repositories.site_repository import site_repository
from models.deployment import Deployment
from utils.logging import logger
from utils.config import settings


# Input Models
class DeploymentInput(AgentInput):
    """Input for deployment."""
    html_code: Optional[str] = Field(None, description="HTML code to deploy (for vanilla sites)")
    files: Optional[Dict[str, str]] = Field(None, description="Files to deploy (for framework sites)")
    site_name: Optional[str] = Field(None, description="Desired site name")
    site_id: Optional[str] = Field(None, description="Site ID for tracking")
    project_id: Optional[str] = Field(None, description="Existing Vercel project ID for updates")
    environment: str = Field(default="production", description="Deployment environment")
    framework: str = Field(default="vanilla", description="Frontend framework (vanilla, react, vue, nextjs, svelte)")
    environment_variables: Optional[Dict[str, str]] = Field(None, description="Environment variables for the deployment")
    
    
# Output Models
class DeploymentMetadata(BaseModel):
    """Metadata about deployment."""
    url: str = Field(..., description="Live deployment URL")
    deployment_id: str = Field(..., description="Vercel deployment ID")
    project_id: str = Field(..., description="Vercel project ID")
    project_name: str = Field(..., description="Project name")
    environment: str = Field(default="production", description="Deployment environment")
    framework: str = Field(default="vanilla", description="Frontend framework used")
    build_config: Optional[Dict[str, Any]] = Field(None, description="Build configuration used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    build_time: Optional[int] = Field(None, description="Build time in milliseconds")
    is_update: bool = Field(default=False, description="Whether this is an update to existing deployment")
    health_check_passed: bool = Field(default=False, description="Whether health check passed")


class DeploymentValidation(BaseModel):
    """Validation results for deployment."""
    is_valid_html: bool = True
    has_content: bool = False
    has_doctype: bool = False
    has_html_tag: bool = False
    has_head: bool = False
    has_body: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class DeploymentOutput(AgentOutput):
    """Output for deployment."""
    deployment_metadata: Optional[DeploymentMetadata] = None
    deployment_validation: Optional[DeploymentValidation] = None
    manual_instructions: Optional[str] = None  # Fallback instructions if automated deployment fails


class DeploymentAgent(BaseAgent):
    """
    Deployment Agent for deploying websites to Vercel.
    
    Responsibilities:
    - Validate HTML before deployment
    - Create or update Vercel projects
    - Deploy sites to production
    - Verify deployment health
    - Store deployment records
    - Generate unique site names
    """
    
    def __init__(self):
        """Initialize Deployment Agent."""
        super().__init__(name="DeploymentAgent")
        self.vercel = vercel_client
        logger.info("Deployment Agent initialized")
    
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute deployment.
        
        Args:
            input_data: Input data with HTML code
            context: Execution context
            
        Returns:
            DeploymentOutput with deployment metadata
            
        Raises:
            AgentError: If deployment fails
        """
        try:
            if not isinstance(input_data, DeploymentInput):
                raise AgentError(
                    message=f"Unsupported input type: {type(input_data).__name__}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            # Parse framework
            try:
                framework = Framework(input_data.framework.lower())
            except ValueError:
                raise AgentError(
                    message=f"Unsupported framework: {input_data.framework}",
                    error_type=ErrorType.VALIDATION_ERROR,
                    agent_name=self.name,
                    recoverable=False,
                    retryable=False,
                )
            
            # Validate deployment content
            logger.info(f"Validating {framework.value} deployment in workflow {context.workflow_id}")
            
            if framework == Framework.VANILLA:
                # Validate HTML for vanilla sites
                if not input_data.html_code:
                    raise AgentError(
                        message="HTML code is required for vanilla deployments",
                        error_type=ErrorType.VALIDATION_ERROR,
                        agent_name=self.name,
                        recoverable=False,
                        retryable=False,
                    )
                validation = self._validate_html(input_data.html_code)
                
                if not validation.is_valid_html:
                    error_msg = f"HTML validation failed: {'; '.join(validation.validation_errors)}"
                    logger.error(error_msg)
                    raise AgentError(
                        message=error_msg,
                        error_type=ErrorType.VALIDATION_ERROR,
                        agent_name=self.name,
                        recoverable=False,
                        retryable=False,
                        context={"validation_errors": validation.validation_errors}
                    )
            else:
                # Validate framework files
                if not input_data.files:
                    raise AgentError(
                        message=f"Files are required for {framework.value} deployments",
                        error_type=ErrorType.VALIDATION_ERROR,
                        agent_name=self.name,
                        recoverable=False,
                        retryable=False,
                    )
                
                # Validate required files are present
                file_list = list(input_data.files.keys())
                is_valid, missing_files = validate_framework_files(framework, file_list)
                
                if not is_valid:
                    raise AgentError(
                        message=f"Missing required files for {framework.value}: {', '.join(missing_files)}",
                        error_type=ErrorType.VALIDATION_ERROR,
                        agent_name=self.name,
                        recoverable=False,
                        retryable=False,
                        context={"missing_files": missing_files}
                    )
                
                # Create a basic validation result for framework deployments
                validation = DeploymentValidation(
                    is_valid_html=True,
                    has_content=True,
                    confidence_score=0.9
                )
            
            # Check if Vercel API token is configured
            if not settings.VERCEL_API_TOKEN:
                logger.warning("Vercel API token not configured, providing manual instructions")
                manual_instructions = self._generate_manual_instructions(
                    input_data.html_code,
                    input_data.site_name
                )
                
                return DeploymentOutput(
                    success=True,
                    deployment_validation=validation,
                    manual_instructions=manual_instructions,
                    confidence=0.5,
                    data={
                        "manual_deployment": True,
                        "instructions": manual_instructions,
                    }
                )
            
            # Generate or use provided site name
            site_name = input_data.site_name or self._generate_site_name()
            logger.info(f"Deploying site: {site_name}")
            
            # Determine if this is an update or new deployment
            is_update = input_data.project_id is not None
            
            # Deploy to Vercel
            deployment_metadata = await self._deploy_to_vercel(
                html_code=input_data.html_code,
                files=input_data.files,
                site_name=site_name,
                project_id=input_data.project_id,
                environment=input_data.environment,
                framework=framework,
                environment_variables=input_data.environment_variables,
                is_update=is_update,
            )
            
            # Store deployment record in database
            if input_data.site_id:
                await self._store_deployment_record(
                    site_id=input_data.site_id,
                    deployment_metadata=deployment_metadata,
                )
            
            logger.info(
                f"Deployment successful for workflow {context.workflow_id}. "
                f"URL: {deployment_metadata.url}"
            )
            
            return DeploymentOutput(
                success=True,
                deployment_metadata=deployment_metadata,
                deployment_validation=validation,
                confidence=validation.confidence_score,
                data={
                    "url": deployment_metadata.url,
                    "deployment_id": deployment_metadata.deployment_id,
                    "project_id": deployment_metadata.project_id,
                    "project_name": deployment_metadata.project_name,
                    "framework": deployment_metadata.framework,
                    "build_config": deployment_metadata.build_config,
                    "build_time": deployment_metadata.build_time,
                    "is_update": deployment_metadata.is_update,
                    "health_check_passed": deployment_metadata.health_check_passed,
                }
            )
            
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Deployment Agent execution error: {str(e)}")
            raise AgentError(
                message=f"Deployment failed: {str(e)}",
                error_type=ErrorType.DEPLOYMENT_ERROR,
                agent_name=self.name,
                recoverable=True,
                retryable=True,
            )
    
    def _validate_html(self, html_code: str) -> DeploymentValidation:
        """
        Validate HTML before deployment.
        
        Args:
            html_code: HTML code to validate
            
        Returns:
            DeploymentValidation with validation results
        """
        validation = DeploymentValidation()
        
        try:
            # Check if HTML has content
            if not html_code or len(html_code.strip()) == 0:
                validation.is_valid_html = False
                validation.validation_errors.append("HTML code is empty")
                return validation
            
            validation.has_content = True
            
            # Check for DOCTYPE
            validation.has_doctype = "<!DOCTYPE" in html_code or "<!doctype" in html_code
            if not validation.has_doctype:
                validation.validation_warnings.append("Missing DOCTYPE declaration")
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_code, 'html.parser')
            
            # Check for essential HTML structure
            html_tag = soup.find('html')
            validation.has_html_tag = html_tag is not None
            if not validation.has_html_tag:
                validation.is_valid_html = False
                validation.validation_errors.append("Missing <html> tag")
            
            head_tag = soup.find('head')
            validation.has_head = head_tag is not None
            if not validation.has_head:
                validation.validation_warnings.append("Missing <head> tag")
            
            body_tag = soup.find('body')
            validation.has_body = body_tag is not None
            if not validation.has_body:
                validation.is_valid_html = False
                validation.validation_errors.append("Missing <body> tag")
            
            # Check for minimum content in body
            if validation.has_body:
                body_text = body_tag.get_text(strip=True)
                if len(body_text) < 10:
                    validation.validation_warnings.append("Body has very little content")
            
            # Calculate confidence score
            validation.confidence_score = self._calculate_validation_confidence(validation)
            
        except Exception as e:
            logger.error(f"Error validating HTML: {str(e)}")
            validation.is_valid_html = False
            validation.validation_errors.append(f"HTML parsing error: {str(e)}")
            validation.confidence_score = 0.0
        
        return validation
    
    def _calculate_validation_confidence(self, validation: DeploymentValidation) -> float:
        """Calculate confidence score based on validation results."""
        score = 0.0
        max_score = 6.0
        
        # Valid HTML structure (most important)
        if validation.is_valid_html:
            score += 2.0
        
        # Has content
        if validation.has_content:
            score += 1.0
        
        # Has DOCTYPE
        if validation.has_doctype:
            score += 0.5
        
        # Has HTML tag
        if validation.has_html_tag:
            score += 1.0
        
        # Has head
        if validation.has_head:
            score += 0.75
        
        # Has body
        if validation.has_body:
            score += 0.75
        
        return score / max_score
    
    def _generate_site_name(self) -> str:
        """
        Generate a unique site name.
        
        Returns:
            Unique site name in format: smart-site-{uuid}
        """
        # Generate short UUID (first 8 characters)
        short_uuid = str(uuid.uuid4())[:8]
        site_name = f"smart-site-{short_uuid}"
        
        logger.info(f"Generated site name: {site_name}")
        return site_name
    
    async def _deploy_to_vercel(
        self,
        site_name: str,
        project_id: Optional[str],
        environment: str,
        framework: Framework,
        is_update: bool,
        html_code: Optional[str] = None,
        files: Optional[Dict[str, str]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> DeploymentMetadata:
        """
        Deploy site to Vercel with retry logic.
        
        Args:
            site_name: Site name
            project_id: Existing project ID (for updates)
            environment: Deployment environment
            framework: Frontend framework
            is_update: Whether this is an update
            html_code: HTML code to deploy (for vanilla sites)
            files: Files to deploy (for framework sites)
            environment_variables: Environment variables for the deployment
            
        Returns:
            DeploymentMetadata with deployment information
            
        Raises:
            AgentError: If deployment fails
        """
        # Track deployment attempt metrics
        deployment_start_time = datetime.utcnow()
        retry_count = 0
        
        def on_retry(attempt: int, error: Exception, delay: float):
            """Callback for retry attempts."""
            nonlocal retry_count
            retry_count = attempt + 1
            logger.warning(
                f"Deployment retry {retry_count}: {str(error)}. "
                f"Waiting {delay:.2f}s before next attempt."
            )
        
        try:
            # Configure retry for transient failures
            retry_config = RetryConfig(
                max_retries=3,
                initial_delay=2.0,
                max_delay=30.0,
                exponential_base=2.0,
                jitter=True,
            )
            
            # Execute deployment with retry logic
            metadata = await retry_with_backoff(
                self._execute_deployment,
                site_name=site_name,
                project_id=project_id,
                environment=environment,
                framework=framework,
                is_update=is_update,
                html_code=html_code,
                files=files,
                environment_variables=environment_variables,
                config=retry_config,
                on_retry=on_retry,
            )
            
            # Calculate total deployment time
            deployment_end_time = datetime.utcnow()
            total_time = (deployment_end_time - deployment_start_time).total_seconds()
            
            logger.info(
                f"Deployment completed successfully after {retry_count} retries. "
                f"Total time: {total_time:.2f}s, Build time: {metadata.build_time}ms"
            )
            
            return metadata
            
        except AgentError:
            raise
        except Exception as e:
            logger.error(f"Deployment failed after all retries: {str(e)}")
            
            # Provide manual deployment instructions as fallback
            manual_instructions = self._generate_manual_instructions(html_code, site_name)
            
            raise AgentError(
                message=(
                    f"Automated deployment failed: {str(e)}. "
                    f"Please deploy manually using the provided instructions."
                ),
                error_type=ErrorType.DEPLOYMENT_ERROR,
                agent_name=self.name,
                recoverable=True,
                retryable=False,
                context={
                    "manual_instructions": manual_instructions,
                    "retry_count": retry_count,
                }
            )
    
    async def _execute_deployment(
        self,
        site_name: str,
        project_id: Optional[str],
        environment: str,
        framework: Framework,
        is_update: bool,
        html_code: Optional[str] = None,
        files: Optional[Dict[str, str]] = None,
        environment_variables: Optional[Dict[str, str]] = None,
    ) -> DeploymentMetadata:
        """
        Execute a single deployment attempt.
        
        This method is called by _deploy_to_vercel with retry logic.
        
        Args:
            site_name: Site name
            project_id: Existing project ID (for updates)
            environment: Deployment environment
            framework: Frontend framework
            is_update: Whether this is an update
            html_code: HTML code to deploy (for vanilla sites)
            files: Files to deploy (for framework sites)
            environment_variables: Environment variables for the deployment
            
        Returns:
            DeploymentMetadata with deployment information
            
        Raises:
            AgentError: If deployment fails
        """
        try:
            # Sanitize site name for Vercel (lowercase, alphanumeric and hyphens only)
            sanitized_name = self._sanitize_site_name(site_name)
            
            # Get framework configuration
            framework_config = get_framework_config(framework)
            logger.info(f"Using {framework.value} framework configuration")
            
            # Get Vercel project settings
            project_settings = get_vercel_project_settings(framework, environment_variables)
            
            # Create or get project
            if project_id:
                logger.info(f"Using existing project: {project_id}")
                try:
                    project = await self.vercel.get_project(project_id)
                    # Update project settings for framework
                    if framework != Framework.VANILLA:
                        logger.info(f"Updating project settings for {framework.value}")
                        project = await self.vercel.update_project(project_id, **project_settings)
                except Exception as e:
                    logger.warning(f"Failed to get existing project, creating new one: {str(e)}")
                    project = await self.vercel.create_project(
                        sanitized_name,
                        framework=framework_config.vercel_config.get("framework", "static")
                    )
            else:
                logger.info(f"Creating new project: {sanitized_name}")
                project = await self.vercel.create_project(
                    sanitized_name,
                    framework=framework_config.vercel_config.get("framework", "static")
                )
            
            # Prepare deployment files
            deployment_files = []
            
            if framework == Framework.VANILLA:
                # For vanilla HTML, just deploy the HTML file
                deployment_files = [
                    {
                        "file": "index.html",
                        "data": html_code,
                    }
                ]
            else:
                # For framework sites, deploy all files
                if files:
                    deployment_files = [
                        {
                            "file": file_path,
                            "data": content,
                        }
                        for file_path, content in files.items()
                    ]
                
                # Add vercel.json for routing configuration
                vercel_config = get_vercel_config_json(framework)
                if vercel_config:
                    import json
                    deployment_files.append({
                        "file": "vercel.json",
                        "data": json.dumps(vercel_config, indent=2),
                    })
            
            # Get build configuration
            build_config = None
            if framework != Framework.VANILLA:
                build_config = {
                    "buildCommand": framework_config.build_command,
                    "outputDirectory": framework_config.output_directory,
                    "installCommand": framework_config.install_command,
                    "framework": framework_config.vercel_config.get("framework"),
                }
            
            # Create deployment
            logger.info(f"Creating {framework.value} deployment for project {project.id}")
            deployment = await self.vercel.create_deployment(
                project_name=project.name,
                files=deployment_files,
                target=environment,
                project_id=project.id,
                build_config=build_config,
            )
            
            # Wait for deployment to complete
            logger.info(f"Waiting for deployment {deployment.id} to complete")
            completed_deployment = await self.vercel.wait_for_deployment(
                deployment_id=deployment.id,
                timeout=300,  # 5 minutes
                poll_interval=5,
            )
            
            # Check deployment state
            if completed_deployment.state == "ERROR":
                raise AgentError(
                    message="Deployment failed on Vercel",
                    error_type=ErrorType.DEPLOYMENT_ERROR,
                    agent_name=self.name,
                    recoverable=True,
                    retryable=True,
                    context={"deployment_id": completed_deployment.id}
                )
            elif completed_deployment.state == "CANCELED":
                raise AgentError(
                    message="Deployment was canceled",
                    error_type=ErrorType.DEPLOYMENT_ERROR,
                    agent_name=self.name,
                    recoverable=True,
                    retryable=True,
                    context={"deployment_id": completed_deployment.id}
                )
            
            # Verify deployment health
            logger.info(f"Verifying deployment health: {completed_deployment.url}")
            health_check_passed = await self.vercel.verify_deployment_health(
                deployment_url=completed_deployment.url,
                timeout=30,
            )
            
            if not health_check_passed:
                logger.warning(f"Deployment health check failed for {completed_deployment.url}")
            
            # Build deployment metadata
            deployment_url = completed_deployment.url
            if not deployment_url.startswith("http"):
                deployment_url = f"https://{deployment_url}"
            
            metadata = DeploymentMetadata(
                url=deployment_url,
                deployment_id=completed_deployment.id,
                project_id=project.id,
                project_name=project.name,
                environment=environment,
                framework=framework.value,
                build_config=build_config,
                timestamp=datetime.utcnow(),
                build_time=completed_deployment.build_time,
                is_update=is_update,
                health_check_passed=health_check_passed,
            )
            
            logger.info(
                f"Deployment completed successfully. "
                f"URL: {metadata.url}, Build time: {metadata.build_time}ms"
            )
            
            return metadata
            
        except AgentError:
            raise
        except TimeoutError as e:
            logger.error(f"Deployment timeout: {str(e)}")
            raise AgentError(
                message=f"Deployment timed out: {str(e)}",
                error_type=ErrorType.TIMEOUT_ERROR,
                agent_name=self.name,
                recoverable=True,
                retryable=True,
            )
        except Exception as e:
            logger.error(f"Error deploying to Vercel: {str(e)}")
            
            # Determine if error is retryable
            is_network_error = isinstance(e, (ConnectionError, TimeoutError))
            
            raise AgentError(
                message=f"Failed to deploy to Vercel: {str(e)}",
                error_type=ErrorType.NETWORK_ERROR if is_network_error else ErrorType.DEPLOYMENT_ERROR,
                agent_name=self.name,
                recoverable=True,
                retryable=is_network_error,
            )
    
    def _sanitize_site_name(self, site_name: str) -> str:
        """
        Sanitize site name for Vercel.
        
        Vercel project names must be lowercase and contain only
        alphanumeric characters and hyphens.
        
        Args:
            site_name: Original site name
            
        Returns:
            Sanitized site name
        """
        # Convert to lowercase
        sanitized = site_name.lower()
        
        # Replace spaces and underscores with hyphens
        sanitized = sanitized.replace(" ", "-").replace("_", "-")
        
        # Remove any characters that aren't alphanumeric or hyphens
        sanitized = re.sub(r'[^a-z0-9-]', '', sanitized)
        
        # Remove consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        
        # Ensure name is not empty
        if not sanitized:
            sanitized = f"site-{str(uuid.uuid4())[:8]}"
        
        # Limit length (Vercel has a max length)
        if len(sanitized) > 63:
            sanitized = sanitized[:63].rstrip('-')
        
        return sanitized
    
    async def _store_deployment_record(
        self,
        site_id: str,
        deployment_metadata: DeploymentMetadata,
    ):
        """
        Store deployment record in database.
        
        Args:
            site_id: Site ID
            deployment_metadata: Deployment metadata
        """
        try:
            logger.info(f"Storing deployment record for site {site_id}")
            
            # Create deployment record
            deployment = Deployment(
                site_id=uuid.UUID(site_id),
                url=deployment_metadata.url,
                deployment_id=deployment_metadata.deployment_id,
                project_id=deployment_metadata.project_id,
                status="success" if deployment_metadata.health_check_passed else "deployed",
                framework=deployment_metadata.framework,
                build_config=deployment_metadata.build_config,
                build_time=deployment_metadata.build_time,
                created_at=deployment_metadata.timestamp,
            )
            
            # Save to database
            await site_repository.save_deployment(deployment)
            
            logger.info(f"Stored deployment record: {deployment.id} (framework: {deployment.framework})")
            
            # Track deployment metrics
            self._track_deployment_metrics(deployment_metadata)
            
        except Exception as e:
            # Log error but don't fail the deployment
            logger.error(f"Error storing deployment record: {str(e)}")
    
    def _track_deployment_metrics(self, deployment_metadata: DeploymentMetadata):
        """
        Track deployment metrics for monitoring.
        
        Args:
            deployment_metadata: Deployment metadata
        """
        try:
            # Log deployment metrics
            logger.info(
                "Deployment metrics",
                extra={
                    "deployment_id": deployment_metadata.deployment_id,
                    "project_id": deployment_metadata.project_id,
                    "framework": deployment_metadata.framework,
                    "build_time_ms": deployment_metadata.build_time,
                    "environment": deployment_metadata.environment,
                    "is_update": deployment_metadata.is_update,
                    "health_check_passed": deployment_metadata.health_check_passed,
                    "timestamp": deployment_metadata.timestamp.isoformat(),
                }
            )
            
            # Calculate success rate (this would typically be stored in a metrics database)
            success_rate = 1.0 if deployment_metadata.health_check_passed else 0.8
            
            logger.info(
                f"Deployment success rate: {success_rate:.2%}, "
                f"Build time: {deployment_metadata.build_time}ms"
            )
            
        except Exception as e:
            logger.error(f"Error tracking deployment metrics: {str(e)}")
    
    def _generate_manual_instructions(
        self,
        html_code: str,
        site_name: Optional[str],
    ) -> str:
        """
        Generate manual deployment instructions as fallback.
        
        Args:
            html_code: HTML code to deploy
            site_name: Optional site name
            
        Returns:
            Manual deployment instructions
        """
        instructions = f"""
# Manual Deployment Instructions

Since automated deployment is not configured, you can deploy your site manually using one of these methods:

## Option 1: Deploy to Vercel (Recommended)

1. Go to https://vercel.com and sign up/login
2. Click "Add New" → "Project"
3. Create a new project{f" named '{site_name}'" if site_name else ""}
4. In your project settings, go to the "Deployments" tab
5. Create a file named `index.html` with the generated code
6. Drag and drop the file to deploy

## Option 2: Deploy to Netlify

1. Go to https://netlify.com and sign up/login
2. Drag and drop your HTML file to the Netlify Drop zone
3. Your site will be live in seconds

## Option 3: Deploy to GitHub Pages

1. Create a new GitHub repository
2. Add your HTML file as `index.html`
3. Go to Settings → Pages
4. Select your branch and save
5. Your site will be available at `https://[username].github.io/[repo-name]`

## Option 4: Use Any Static Hosting

You can deploy the generated HTML to any static hosting service:
- Cloudflare Pages
- AWS S3 + CloudFront
- Google Cloud Storage
- Azure Static Web Apps

## Your Generated HTML

The HTML code has been generated and validated. You can copy it from the preview
or download it to deploy manually.

## Configure Automated Deployment

To enable automated deployment in the future, set the `VERCEL_API_TOKEN` environment
variable with your Vercel API token. You can get a token from:
https://vercel.com/account/tokens
"""
        
        return instructions.strip()
    
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate Deployment Agent output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        result = ValidationResult(is_valid=True, confidence=1.0)
        
        if not output.success:
            result.add_error("Operation failed")
            return result
        
        if not isinstance(output, DeploymentOutput):
            result.add_error("Invalid output type")
            return result
        
        # Check if we have either deployment metadata or manual instructions
        if not output.deployment_metadata and not output.manual_instructions:
            result.add_error("No deployment metadata or manual instructions in output")
            return result
        
        # If we have deployment metadata, validate it
        if output.deployment_metadata:
            metadata = output.deployment_metadata
            
            # Check required fields
            if not metadata.url:
                result.add_error("Missing deployment URL")
            
            if not metadata.deployment_id:
                result.add_error("Missing deployment ID")
            
            if not metadata.project_id:
                result.add_error("Missing project ID")
            
            # Check URL format
            if metadata.url and not (
                metadata.url.startswith("http://") or 
                metadata.url.startswith("https://")
            ):
                result.add_warning("Deployment URL should start with http:// or https://")
            
            # Check health check
            if not metadata.health_check_passed:
                result.add_warning("Deployment health check did not pass")
            
            # Set confidence based on validation
            if output.deployment_validation:
                result.confidence = output.deployment_validation.confidence_score
        
        # If we only have manual instructions, lower confidence
        if output.manual_instructions and not output.deployment_metadata:
            result.confidence = 0.5
            result.add_warning("Automated deployment not available, manual instructions provided")
        
        return result


# Global deployment agent instance
deployment_agent = DeploymentAgent()
