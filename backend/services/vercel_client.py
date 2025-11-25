"""
Vercel API client for deployment operations.

This client provides a wrapper around the Vercel REST API for:
- Creating and updating projects
- Deploying static sites
- Checking deployment status
- Managing project configurations
"""
import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field

from utils.config import settings
from utils.logging import logger


class VercelProject(BaseModel):
    """Vercel project information."""
    id: str
    name: str
    account_id: str
    created_at: int
    framework: Optional[str] = None
    
    
class VercelDeployment(BaseModel):
    """Vercel deployment information."""
    id: str
    url: str
    project_id: str
    state: str  # BUILDING, READY, ERROR, CANCELED
    created_at: int
    ready: Optional[int] = None
    build_time: Optional[int] = None  # milliseconds
    
    
class VercelFile(BaseModel):
    """File to be deployed to Vercel."""
    file: str  # Path in the deployment
    data: str  # Base64 encoded content or raw content
    encoding: str = "utf-8"  # utf-8 or base64


class VercelDeploymentRequest(BaseModel):
    """Request to create a Vercel deployment."""
    name: str
    files: List[Dict[str, str]]
    project_settings: Optional[Dict[str, Any]] = None
    target: str = "production"  # production or preview


class VercelClient:
    """
    Client for interacting with Vercel API.
    
    Provides methods for:
    - Project creation and management
    - Deployment operations
    - Status polling
    - Health verification
    """
    
    BASE_URL = "https://api.vercel.com"
    API_VERSION = "v13"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Vercel client.
        
        Args:
            api_token: Vercel API token (defaults to settings.VERCEL_API_TOKEN)
        """
        self.api_token = api_token or settings.VERCEL_API_TOKEN
        
        if not self.api_token:
            logger.warning("Vercel API token not configured")
        
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self._get_headers(),
            timeout=60.0,
        )
        
        logger.info("Vercel client initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Vercel API requests."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def create_project(
        self,
        name: str,
        framework: str = "static",
        **kwargs
    ) -> VercelProject:
        """
        Create a new Vercel project.
        
        Args:
            name: Project name (must be unique)
            framework: Framework type (default: static)
            **kwargs: Additional project settings
            
        Returns:
            VercelProject with project information
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(f"Creating Vercel project: {name}")
            
            payload = {
                "name": name,
                "framework": framework,
                **kwargs
            }
            
            response = await self.client.post(
                f"/{self.API_VERSION}/projects",
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            project = VercelProject(
                id=data["id"],
                name=data["name"],
                account_id=data["accountId"],
                created_at=data["createdAt"],
                framework=data.get("framework"),
            )
            
            logger.info(f"Created Vercel project: {project.id}")
            return project
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                # Project already exists, try to get it
                logger.info(f"Project {name} already exists, fetching existing project")
                return await self.get_project(name)
            else:
                logger.error(f"Failed to create project: {e.response.text}")
                raise
        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise
    
    async def get_project(self, name_or_id: str) -> VercelProject:
        """
        Get project by name or ID.
        
        Args:
            name_or_id: Project name or ID
            
        Returns:
            VercelProject with project information
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(f"Fetching Vercel project: {name_or_id}")
            
            response = await self.client.get(
                f"/{self.API_VERSION}/projects/{name_or_id}"
            )
            
            response.raise_for_status()
            data = response.json()
            
            project = VercelProject(
                id=data["id"],
                name=data["name"],
                account_id=data["accountId"],
                created_at=data["createdAt"],
                framework=data.get("framework"),
            )
            
            return project
            
        except Exception as e:
            logger.error(f"Error fetching project: {str(e)}")
            raise
    
    async def update_project(
        self,
        project_id: str,
        **settings
    ) -> VercelProject:
        """
        Update project settings.
        
        Args:
            project_id: Project ID
            **settings: Settings to update
            
        Returns:
            Updated VercelProject
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(f"Updating Vercel project: {project_id}")
            
            response = await self.client.patch(
                f"/{self.API_VERSION}/projects/{project_id}",
                json=settings
            )
            
            response.raise_for_status()
            data = response.json()
            
            project = VercelProject(
                id=data["id"],
                name=data["name"],
                account_id=data["accountId"],
                created_at=data["createdAt"],
                framework=data.get("framework"),
            )
            
            logger.info(f"Updated Vercel project: {project.id}")
            return project
            
        except Exception as e:
            logger.error(f"Error updating project: {str(e)}")
            raise
    
    async def create_deployment(
        self,
        project_name: str,
        html_content: Optional[str] = None,
        files: Optional[List[Dict[str, str]]] = None,
        target: str = "production",
        project_id: Optional[str] = None,
        build_config: Optional[Dict[str, Any]] = None,
    ) -> VercelDeployment:
        """
        Create a new deployment.
        
        Args:
            project_name: Project name
            html_content: HTML content to deploy (for vanilla HTML sites)
            files: List of files to deploy (for framework-based sites)
            target: Deployment target (production or preview)
            project_id: Optional project ID (will be fetched if not provided)
            build_config: Optional build configuration (buildCommand, outputDirectory, etc.)
            
        Returns:
            VercelDeployment with deployment information
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(f"Creating deployment for project: {project_name}")
            
            # Prepare files for deployment
            if files:
                deployment_files = files
            elif html_content:
                deployment_files = [
                    {
                        "file": "index.html",
                        "data": html_content,
                    }
                ]
            else:
                raise ValueError("Either html_content or files must be provided")
            
            # Build deployment payload
            payload = {
                "name": project_name,
                "files": deployment_files,
                "target": target,
            }
            
            if project_id:
                payload["projectId"] = project_id
            
            # Add build configuration if provided
            if build_config:
                payload["projectSettings"] = build_config
            
            # Create deployment
            response = await self.client.post(
                f"/{self.API_VERSION}/deployments",
                json=payload
            )
            
            response.raise_for_status()
            data = response.json()
            
            deployment = VercelDeployment(
                id=data["id"],
                url=data["url"],
                project_id=data.get("projectId", project_id or ""),
                state=data.get("readyState", "BUILDING"),
                created_at=data["createdAt"],
            )
            
            logger.info(
                f"Created deployment: {deployment.id} "
                f"(URL: https://{deployment.url})"
            )
            
            return deployment
            
        except Exception as e:
            logger.error(f"Error creating deployment: {str(e)}")
            raise
    
    async def get_deployment(self, deployment_id: str) -> VercelDeployment:
        """
        Get deployment status.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            VercelDeployment with current status
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            response = await self.client.get(
                f"/{self.API_VERSION}/deployments/{deployment_id}"
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Calculate build time if deployment is ready
            build_time = None
            if data.get("ready") and data.get("createdAt"):
                build_time = data["ready"] - data["createdAt"]
            
            deployment = VercelDeployment(
                id=data["id"],
                url=data["url"],
                project_id=data.get("projectId", ""),
                state=data.get("readyState", "BUILDING"),
                created_at=data["createdAt"],
                ready=data.get("ready"),
                build_time=build_time,
            )
            
            return deployment
            
        except Exception as e:
            logger.error(f"Error fetching deployment: {str(e)}")
            raise
    
    async def wait_for_deployment(
        self,
        deployment_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> VercelDeployment:
        """
        Wait for deployment to complete.
        
        Polls the deployment status until it reaches a terminal state
        (READY, ERROR, or CANCELED) or timeout is reached.
        
        Args:
            deployment_id: Deployment ID
            timeout: Maximum time to wait in seconds (default: 300)
            poll_interval: Time between polls in seconds (default: 5)
            
        Returns:
            VercelDeployment with final status
            
        Raises:
            TimeoutError: If deployment doesn't complete within timeout
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(
                f"Waiting for deployment {deployment_id} "
                f"(timeout: {timeout}s, poll interval: {poll_interval}s)"
            )
            
            start_time = time.time()
            terminal_states = {"READY", "ERROR", "CANCELED"}
            
            while True:
                # Check timeout
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    raise TimeoutError(
                        f"Deployment {deployment_id} did not complete within {timeout}s"
                    )
                
                # Get deployment status
                deployment = await self.get_deployment(deployment_id)
                
                logger.debug(
                    f"Deployment {deployment_id} state: {deployment.state} "
                    f"(elapsed: {elapsed:.1f}s)"
                )
                
                # Check if deployment reached terminal state
                if deployment.state in terminal_states:
                    logger.info(
                        f"Deployment {deployment_id} completed with state: {deployment.state}"
                    )
                    return deployment
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
                
        except TimeoutError:
            raise
        except Exception as e:
            logger.error(f"Error waiting for deployment: {str(e)}")
            raise
    
    async def verify_deployment_health(
        self,
        deployment_url: str,
        timeout: int = 30,
    ) -> bool:
        """
        Verify deployment is accessible and healthy.
        
        Args:
            deployment_url: Deployment URL to check
            timeout: Request timeout in seconds
            
        Returns:
            True if deployment is healthy, False otherwise
        """
        try:
            logger.info(f"Verifying deployment health: {deployment_url}")
            
            # Ensure URL has protocol
            if not deployment_url.startswith("http"):
                deployment_url = f"https://{deployment_url}"
            
            # Make health check request
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(deployment_url)
                
                # Check if response is successful
                is_healthy = response.status_code == 200
                
                if is_healthy:
                    logger.info(f"Deployment is healthy: {deployment_url}")
                else:
                    logger.warning(
                        f"Deployment health check failed: {deployment_url} "
                        f"(status: {response.status_code})"
                    )
                
                return is_healthy
                
        except Exception as e:
            logger.error(f"Error verifying deployment health: {str(e)}")
            return False
    
    async def list_deployments(
        self,
        project_id: str,
        limit: int = 20,
    ) -> List[VercelDeployment]:
        """
        List deployments for a project.
        
        Args:
            project_id: Project ID
            limit: Maximum number of deployments to return
            
        Returns:
            List of VercelDeployment objects
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(f"Listing deployments for project: {project_id}")
            
            response = await self.client.get(
                f"/{self.API_VERSION}/deployments",
                params={
                    "projectId": project_id,
                    "limit": limit,
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            deployments = []
            for item in data.get("deployments", []):
                # Calculate build time if available
                build_time = None
                if item.get("ready") and item.get("createdAt"):
                    build_time = item["ready"] - item["createdAt"]
                
                deployment = VercelDeployment(
                    id=item["id"],
                    url=item["url"],
                    project_id=item.get("projectId", project_id),
                    state=item.get("readyState", "UNKNOWN"),
                    created_at=item["createdAt"],
                    ready=item.get("ready"),
                    build_time=build_time,
                )
                deployments.append(deployment)
            
            logger.info(f"Found {len(deployments)} deployments for project {project_id}")
            return deployments
            
        except Exception as e:
            logger.error(f"Error listing deployments: {str(e)}")
            raise
    
    async def delete_deployment(self, deployment_id: str) -> bool:
        """
        Delete a deployment.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            True if deletion was successful
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        try:
            logger.info(f"Deleting deployment: {deployment_id}")
            
            response = await self.client.delete(
                f"/{self.API_VERSION}/deployments/{deployment_id}"
            )
            
            response.raise_for_status()
            
            logger.info(f"Deleted deployment: {deployment_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting deployment: {str(e)}")
            raise


# Global Vercel client instance
vercel_client = VercelClient()
