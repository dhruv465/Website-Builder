"""
Integration repository for database operations.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.integration import Integration
from utils.logging import logger


class IntegrationRepository:
    """Repository for integration database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create(
        self,
        site_id: UUID,
        integration_type: str,
        provider: str,
        html_snippet: str,
        javascript_snippet: Optional[str] = None,
        css_snippet: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        config: Optional[dict] = None,
        setup_instructions: Optional[dict] = None,
        is_secure: bool = True,
        security_issues: Optional[List[str]] = None,
        security_warnings: Optional[List[str]] = None,
        security_recommendations: Optional[List[str]] = None,
        confidence_score: Optional[float] = None,
    ) -> Integration:
        """
        Create a new integration.
        
        Args:
            site_id: Site ID
            integration_type: Type of integration (payment, booking, contact)
            provider: Integration provider
            html_snippet: HTML code snippet
            javascript_snippet: JavaScript code snippet (optional)
            css_snippet: CSS code snippet (optional)
            dependencies: List of CDN dependencies (optional)
            config: Provider-specific configuration (optional)
            setup_instructions: Setup instructions (optional)
            is_secure: Whether integration is secure
            security_issues: List of security issues (optional)
            security_warnings: List of security warnings (optional)
            security_recommendations: List of security recommendations (optional)
            confidence_score: Confidence score (optional)
            
        Returns:
            Created Integration object
        """
        try:
            integration = Integration(
                site_id=site_id,
                integration_type=integration_type,
                provider=provider,
                html_snippet=html_snippet,
                javascript_snippet=javascript_snippet,
                css_snippet=css_snippet,
                dependencies=dependencies or [],
                config=config or {},
                setup_instructions=setup_instructions or {},
                is_secure=is_secure,
                security_issues=security_issues or [],
                security_warnings=security_warnings or [],
                security_recommendations=security_recommendations or [],
                confidence_score=str(confidence_score) if confidence_score is not None else None,
                is_active=True,
            )
            
            self.db.add(integration)
            self.db.commit()
            self.db.refresh(integration)
            
            logger.info(f"Created integration {integration.id} for site {site_id}")
            return integration
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating integration: {str(e)}")
            raise
    
    def get_by_id(self, integration_id: UUID) -> Optional[Integration]:
        """
        Get integration by ID.
        
        Args:
            integration_id: Integration ID
            
        Returns:
            Integration object or None if not found
        """
        try:
            return self.db.query(Integration).filter(
                Integration.id == integration_id
            ).first()
        except Exception as e:
            logger.error(f"Error getting integration {integration_id}: {str(e)}")
            raise
    
    def get_by_site_id(
        self,
        site_id: UUID,
        active_only: bool = True
    ) -> List[Integration]:
        """
        Get all integrations for a site.
        
        Args:
            site_id: Site ID
            active_only: Only return active integrations
            
        Returns:
            List of Integration objects
        """
        try:
            query = self.db.query(Integration).filter(
                Integration.site_id == site_id
            )
            
            if active_only:
                query = query.filter(Integration.is_active == True)
            
            return query.order_by(desc(Integration.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error getting integrations for site {site_id}: {str(e)}")
            raise
    
    def get_by_type(
        self,
        site_id: UUID,
        integration_type: str,
        active_only: bool = True
    ) -> List[Integration]:
        """
        Get integrations by type for a site.
        
        Args:
            site_id: Site ID
            integration_type: Type of integration
            active_only: Only return active integrations
            
        Returns:
            List of Integration objects
        """
        try:
            query = self.db.query(Integration).filter(
                Integration.site_id == site_id,
                Integration.integration_type == integration_type
            )
            
            if active_only:
                query = query.filter(Integration.is_active == True)
            
            return query.order_by(desc(Integration.created_at)).all()
            
        except Exception as e:
            logger.error(
                f"Error getting {integration_type} integrations for site {site_id}: {str(e)}"
            )
            raise
    
    def update(
        self,
        integration_id: UUID,
        **kwargs
    ) -> Optional[Integration]:
        """
        Update an integration.
        
        Args:
            integration_id: Integration ID
            **kwargs: Fields to update
            
        Returns:
            Updated Integration object or None if not found
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return None
            
            for key, value in kwargs.items():
                if hasattr(integration, key):
                    setattr(integration, key, value)
            
            self.db.commit()
            self.db.refresh(integration)
            
            logger.info(f"Updated integration {integration_id}")
            return integration
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating integration {integration_id}: {str(e)}")
            raise
    
    def deactivate(self, integration_id: UUID) -> bool:
        """
        Deactivate an integration (soft delete).
        
        Args:
            integration_id: Integration ID
            
        Returns:
            True if successful, False if not found
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return False
            
            integration.is_active = False
            self.db.commit()
            
            logger.info(f"Deactivated integration {integration_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deactivating integration {integration_id}: {str(e)}")
            raise
    
    def delete(self, integration_id: UUID) -> bool:
        """
        Permanently delete an integration.
        
        Args:
            integration_id: Integration ID
            
        Returns:
            True if successful, False if not found
        """
        try:
            integration = self.get_by_id(integration_id)
            if not integration:
                return False
            
            self.db.delete(integration)
            self.db.commit()
            
            logger.info(f"Deleted integration {integration_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting integration {integration_id}: {str(e)}")
            raise
    
    def count_by_site(self, site_id: UUID, active_only: bool = True) -> int:
        """
        Count integrations for a site.
        
        Args:
            site_id: Site ID
            active_only: Only count active integrations
            
        Returns:
            Number of integrations
        """
        try:
            query = self.db.query(Integration).filter(
                Integration.site_id == site_id
            )
            
            if active_only:
                query = query.filter(Integration.is_active == True)
            
            return query.count()
            
        except Exception as e:
            logger.error(f"Error counting integrations for site {site_id}: {str(e)}")
            raise
