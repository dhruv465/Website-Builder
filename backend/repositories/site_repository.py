"""
Site repository for database operations.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session as DBSession, joinedload
from sqlalchemy import and_, desc
from contextlib import contextmanager
import uuid

from models.site import Site, SiteVersion, FrameworkChange, FrameworkTypeDB, DesignStyleTypeDB
from models.audit import Audit
from models.deployment import Deployment
from models.base import get_db
from utils.logging import logger


class SiteRepository:
    """Repository for site database operations with transaction management."""
    
    def __init__(self, db: Optional[DBSession] = None):
        """
        Initialize repository.
        
        Args:
            db: Database session (optional, will create new if not provided)
        """
        self.db = db
    
    @contextmanager
    def _get_db_context(self):
        """
        Get database session context.
        Uses provided session or creates a new one with transaction management.
        """
        if self.db:
            # Use provided session, caller manages transaction
            yield self.db
        else:
            # Create new session with automatic transaction management
            with get_db() as db:
                yield db
    
    def create_site(
        self,
        session_id: uuid.UUID,
        name: str,
        framework: Optional[FrameworkTypeDB] = None,
        design_style: Optional[DesignStyleTypeDB] = None,
    ) -> Site:
        """
        Create a new site.
        
        Args:
            session_id: Session ID
            name: Site name
            framework: Framework type
            design_style: Design style type
            
        Returns:
            Created site
        """
        try:
            with self._get_db_context() as db:
                site = Site(
                    session_id=session_id,
                    name=name,
                    framework=framework,
                    design_style=design_style,
                )
                db.add(site)
                if not self.db:
                    db.commit()
                db.refresh(site)
                logger.info(f"Created site {site.id} for session {session_id} with framework {framework} and design style {design_style}")
                return site
        except Exception as e:
            logger.error(f"Error creating site: {str(e)}")
            raise
    
    def get_site_by_id(self, site_id: uuid.UUID) -> Optional[Site]:
        """
        Get site by ID with all relationships.
        
        Args:
            site_id: Site ID
            
        Returns:
            Site or None if not found
        """
        try:
            with self._get_db_context() as db:
                site = db.query(Site).options(
                    joinedload(Site.versions),
                    joinedload(Site.audits),
                    joinedload(Site.deployments),
                ).filter(Site.id == site_id).first()
                return site
        except Exception as e:
            logger.error(f"Error getting site {site_id}: {str(e)}")
            return None
    
    def get_sites_by_session(self, session_id: uuid.UUID) -> List[Site]:
        """
        Get all sites for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of sites
        """
        try:
            with self._get_db_context() as db:
                sites = db.query(Site).filter(
                    Site.session_id == session_id
                ).order_by(desc(Site.updated_at)).all()
                return sites
        except Exception as e:
            logger.error(f"Error getting sites for session {session_id}: {str(e)}")
            return []
    
    def update_site(
        self,
        site_id: uuid.UUID,
        name: Optional[str] = None,
        framework: Optional[FrameworkTypeDB] = None,
        design_style: Optional[DesignStyleTypeDB] = None,
    ) -> Optional[Site]:
        """
        Update site.
        
        Args:
            site_id: Site ID
            name: Updated name
            framework: Updated framework type
            design_style: Updated design style type
            
        Returns:
            Updated site or None if not found
        """
        try:
            with self._get_db_context() as db:
                site = db.query(Site).filter(Site.id == site_id).first()
                if not site:
                    return None
                
                # Track framework change if framework is being updated
                if framework is not None and framework != site.framework:
                    self._create_framework_change(
                        db=db,
                        site_id=site_id,
                        from_framework=site.framework,
                        to_framework=framework,
                        reason="User requested framework change"
                    )
                
                if name is not None:
                    site.name = name
                if framework is not None:
                    site.framework = framework
                if design_style is not None:
                    site.design_style = design_style
                
                site.updated_at = datetime.utcnow()
                if not self.db:
                    db.commit()
                db.refresh(site)
                logger.info(f"Updated site {site_id}")
                return site
        except Exception as e:
            logger.error(f"Error updating site {site_id}: {str(e)}")
            raise
    
    def delete_site(self, site_id: uuid.UUID) -> bool:
        """
        Delete site and all related data.
        
        Args:
            site_id: Site ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_db_context() as db:
                site = db.query(Site).filter(Site.id == site_id).first()
                if not site:
                    return False
                
                db.delete(site)
                if not self.db:
                    db.commit()
                logger.info(f"Deleted site {site_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting site {site_id}: {str(e)}")
            raise
    
    def create_version(
        self,
        site_id: uuid.UUID,
        code: str,
        requirements: Optional[dict] = None,
        changes: Optional[str] = None,
    ) -> SiteVersion:
        """
        Create a new site version.
        
        Args:
            site_id: Site ID
            code: HTML code
            requirements: Site requirements
            changes: Description of changes
            
        Returns:
            Created site version
        """
        try:
            with self._get_db_context() as db:
                # Get the latest version number
                latest_version = db.query(SiteVersion).filter(
                    SiteVersion.site_id == site_id
                ).order_by(desc(SiteVersion.version_number)).first()
                
                version_number = 1 if not latest_version else latest_version.version_number + 1
                
                version = SiteVersion(
                    site_id=site_id,
                    version_number=version_number,
                    code=code,
                    requirements=requirements,
                    changes=changes,
                )
                db.add(version)
                
                # Update site's updated_at timestamp
                site = db.query(Site).filter(Site.id == site_id).first()
                if site:
                    site.updated_at = datetime.utcnow()
                
                if not self.db:
                    db.commit()
                db.refresh(version)
                logger.info(f"Created version {version_number} for site {site_id}")
                return version
        except Exception as e:
            logger.error(f"Error creating site version: {str(e)}")
            raise
    
    def get_version_by_id(self, version_id: uuid.UUID) -> Optional[SiteVersion]:
        """
        Get site version by ID.
        
        Args:
            version_id: Version ID
            
        Returns:
            Site version or None if not found
        """
        try:
            with self._get_db_context() as db:
                version = db.query(SiteVersion).filter(
                    SiteVersion.id == version_id
                ).first()
                return version
        except Exception as e:
            logger.error(f"Error getting version {version_id}: {str(e)}")
            return None
    
    def get_versions_by_site(self, site_id: uuid.UUID) -> List[SiteVersion]:
        """
        Get all versions for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            List of site versions ordered by version number descending
        """
        try:
            with self._get_db_context() as db:
                versions = db.query(SiteVersion).filter(
                    SiteVersion.site_id == site_id
                ).order_by(desc(SiteVersion.version_number)).all()
                return versions
        except Exception as e:
            logger.error(f"Error getting versions for site {site_id}: {str(e)}")
            return []
    
    def get_latest_version(self, site_id: uuid.UUID) -> Optional[SiteVersion]:
        """
        Get the latest version for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            Latest site version or None if no versions exist
        """
        try:
            with self._get_db_context() as db:
                version = db.query(SiteVersion).filter(
                    SiteVersion.site_id == site_id
                ).order_by(desc(SiteVersion.version_number)).first()
                return version
        except Exception as e:
            logger.error(f"Error getting latest version for site {site_id}: {str(e)}")
            return None
    
    def update_version_audit_score(
        self,
        version_id: uuid.UUID,
        audit_score: float,
    ) -> Optional[SiteVersion]:
        """
        Update version audit score.
        
        Args:
            version_id: Version ID
            audit_score: Audit score
            
        Returns:
            Updated version or None if not found
        """
        try:
            with self._get_db_context() as db:
                version = db.query(SiteVersion).filter(
                    SiteVersion.id == version_id
                ).first()
                if not version:
                    return None
                
                version.audit_score = audit_score
                if not self.db:
                    db.commit()
                db.refresh(version)
                logger.info(f"Updated audit score for version {version_id}")
                return version
        except Exception as e:
            logger.error(f"Error updating version audit score: {str(e)}")
            raise
    
    def get_audits_by_site(self, site_id: uuid.UUID) -> List[Audit]:
        """
        Get all audits for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            List of audits ordered by creation date descending
        """
        try:
            with self._get_db_context() as db:
                audits = db.query(Audit).filter(
                    Audit.site_id == site_id
                ).order_by(desc(Audit.created_at)).all()
                return audits
        except Exception as e:
            logger.error(f"Error getting audits for site {site_id}: {str(e)}")
            return []
    
    def get_deployments_by_site(self, site_id: uuid.UUID) -> List[Deployment]:
        """
        Get all deployments for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            List of deployments ordered by creation date descending
        """
        try:
            with self._get_db_context() as db:
                deployments = db.query(Deployment).filter(
                    Deployment.site_id == site_id
                ).order_by(desc(Deployment.created_at)).all()
                return deployments
        except Exception as e:
            logger.error(f"Error getting deployments for site {site_id}: {str(e)}")
            return []
    
    async def save_deployment(self, deployment: Deployment) -> Deployment:
        """
        Save a deployment record.
        
        Args:
            deployment: Deployment to save
            
        Returns:
            Saved deployment
        """
        try:
            with self._get_db_context() as db:
                db.add(deployment)
                if not self.db:
                    db.commit()
                db.refresh(deployment)
                logger.info(f"Saved deployment {deployment.id} for site {deployment.site_id}")
                return deployment
        except Exception as e:
            logger.error(f"Error saving deployment: {str(e)}")
            raise
    
    def _create_framework_change(
        self,
        db: DBSession,
        site_id: uuid.UUID,
        from_framework: Optional[FrameworkTypeDB],
        to_framework: FrameworkTypeDB,
        reason: Optional[str] = None,
    ) -> FrameworkChange:
        """
        Create a framework change record (internal method).
        
        Args:
            db: Database session
            site_id: Site ID
            from_framework: Previous framework
            to_framework: New framework
            reason: Reason for change
            
        Returns:
            Created framework change record
        """
        change = FrameworkChange(
            site_id=site_id,
            from_framework=from_framework,
            to_framework=to_framework,
            reason=reason,
        )
        db.add(change)
        logger.info(f"Tracked framework change for site {site_id}: {from_framework} -> {to_framework}")
        return change
    
    def create_framework_change(
        self,
        site_id: uuid.UUID,
        from_framework: Optional[FrameworkTypeDB],
        to_framework: FrameworkTypeDB,
        reason: Optional[str] = None,
    ) -> FrameworkChange:
        """
        Create a framework change record.
        
        Args:
            site_id: Site ID
            from_framework: Previous framework
            to_framework: New framework
            reason: Reason for change
            
        Returns:
            Created framework change record
        """
        try:
            with self._get_db_context() as db:
                change = self._create_framework_change(
                    db=db,
                    site_id=site_id,
                    from_framework=from_framework,
                    to_framework=to_framework,
                    reason=reason,
                )
                if not self.db:
                    db.commit()
                db.refresh(change)
                return change
        except Exception as e:
            logger.error(f"Error creating framework change: {str(e)}")
            raise
    
    def get_framework_changes(self, site_id: uuid.UUID) -> List[FrameworkChange]:
        """
        Get all framework changes for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            List of framework changes ordered by creation date descending
        """
        try:
            with self._get_db_context() as db:
                changes = db.query(FrameworkChange).filter(
                    FrameworkChange.site_id == site_id
                ).order_by(desc(FrameworkChange.created_at)).all()
                return changes
        except Exception as e:
            logger.error(f"Error getting framework changes for site {site_id}: {str(e)}")
            return []


# Global site repository instance
site_repository = SiteRepository()
