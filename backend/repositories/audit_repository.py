"""
Audit repository for database operations.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession, joinedload
from sqlalchemy import and_, desc, func
from contextlib import contextmanager
import uuid

from models.audit import Audit, AuditIssue, SeverityLevel
from models.base import get_db
from utils.logging import logger


class AuditRepository:
    """Repository for audit database operations with transaction management."""
    
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
    
    def create_audit(
        self,
        site_id: uuid.UUID,
        site_version_id: Optional[uuid.UUID],
        seo_score: int,
        accessibility_score: int,
        performance_score: int,
        overall_score: int,
        details: Optional[Dict[str, Any]] = None,
    ) -> Audit:
        """
        Create a new audit.
        
        Args:
            site_id: Site ID
            site_version_id: Site version ID (optional)
            seo_score: SEO score (0-100)
            accessibility_score: Accessibility score (0-100)
            performance_score: Performance score (0-100)
            overall_score: Overall score (0-100)
            details: Additional audit details
            
        Returns:
            Created audit
        """
        try:
            with self._get_db_context() as db:
                audit = Audit(
                    site_id=site_id,
                    site_version_id=site_version_id,
                    seo_score=seo_score,
                    accessibility_score=accessibility_score,
                    performance_score=performance_score,
                    overall_score=overall_score,
                    details=details,
                )
                db.add(audit)
                if not self.db:
                    db.commit()
                db.refresh(audit)
                logger.info(f"Created audit {audit.id} for site {site_id}")
                return audit
        except Exception as e:
            logger.error(f"Error creating audit: {str(e)}")
            raise
    
    def create_audit_issue(
        self,
        audit_id: uuid.UUID,
        category: str,
        severity: SeverityLevel,
        description: str,
        location: Optional[str] = None,
        fix_suggestion: Optional[str] = None,
    ) -> AuditIssue:
        """
        Create an audit issue.
        
        Args:
            audit_id: Audit ID
            category: Issue category (seo, accessibility, performance)
            severity: Issue severity
            description: Issue description
            location: Location in code
            fix_suggestion: Suggested fix
            
        Returns:
            Created audit issue
        """
        try:
            with self._get_db_context() as db:
                issue = AuditIssue(
                    audit_id=audit_id,
                    category=category,
                    severity=severity,
                    description=description,
                    location=location,
                    fix_suggestion=fix_suggestion,
                )
                db.add(issue)
                if not self.db:
                    db.commit()
                db.refresh(issue)
                logger.debug(f"Created audit issue {issue.id} for audit {audit_id}")
                return issue
        except Exception as e:
            logger.error(f"Error creating audit issue: {str(e)}")
            raise
    
    def get_audit_by_id(self, audit_id: uuid.UUID) -> Optional[Audit]:
        """
        Get audit by ID with all issues.
        
        Args:
            audit_id: Audit ID
            
        Returns:
            Audit or None if not found
        """
        try:
            with self._get_db_context() as db:
                audit = db.query(Audit).options(
                    joinedload(Audit.issues)
                ).filter(Audit.id == audit_id).first()
                return audit
        except Exception as e:
            logger.error(f"Error getting audit {audit_id}: {str(e)}")
            return None
    
    def get_audits_by_site(
        self,
        site_id: uuid.UUID,
        limit: Optional[int] = None
    ) -> List[Audit]:
        """
        Get all audits for a site.
        
        Args:
            site_id: Site ID
            limit: Maximum number of audits to return
            
        Returns:
            List of audits ordered by creation date descending
        """
        try:
            with self._get_db_context() as db:
                query = db.query(Audit).options(
                    joinedload(Audit.issues)
                ).filter(
                    Audit.site_id == site_id
                ).order_by(desc(Audit.created_at))
                
                if limit:
                    query = query.limit(limit)
                
                audits = query.all()
                return audits
        except Exception as e:
            logger.error(f"Error getting audits for site {site_id}: {str(e)}")
            return []
    
    def get_latest_audit(self, site_id: uuid.UUID) -> Optional[Audit]:
        """
        Get the latest audit for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            Latest audit or None if no audits exist
        """
        try:
            with self._get_db_context() as db:
                audit = db.query(Audit).options(
                    joinedload(Audit.issues)
                ).filter(
                    Audit.site_id == site_id
                ).order_by(desc(Audit.created_at)).first()
                return audit
        except Exception as e:
            logger.error(f"Error getting latest audit for site {site_id}: {str(e)}")
            return None
    
    def get_audit_trends(
        self,
        site_id: uuid.UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get audit trends for a site over time.
        
        Args:
            site_id: Site ID
            days: Number of days to look back
            
        Returns:
            Dictionary with trend data
        """
        try:
            with self._get_db_context() as db:
                # Get audits from the last N days
                since_date = datetime.utcnow() - timedelta(days=days)
                audits = db.query(Audit).filter(
                    and_(
                        Audit.site_id == site_id,
                        Audit.created_at >= since_date
                    )
                ).order_by(Audit.created_at).all()
                
                if not audits:
                    return {
                        "site_id": str(site_id),
                        "period_days": days,
                        "audit_count": 0,
                        "trends": [],
                        "average_scores": {},
                        "improvement": {}
                    }
                
                # Extract trend data
                trends = []
                for audit in audits:
                    trends.append({
                        "timestamp": audit.created_at.isoformat(),
                        "overall_score": audit.overall_score,
                        "seo_score": audit.seo_score,
                        "accessibility_score": audit.accessibility_score,
                        "performance_score": audit.performance_score,
                    })
                
                # Calculate average scores
                avg_overall = sum(a.overall_score for a in audits) / len(audits)
                avg_seo = sum(a.seo_score for a in audits) / len(audits)
                avg_accessibility = sum(a.accessibility_score for a in audits) / len(audits)
                avg_performance = sum(a.performance_score for a in audits) / len(audits)
                
                # Calculate improvement (first vs last)
                first_audit = audits[0]
                last_audit = audits[-1]
                improvement = {
                    "overall": last_audit.overall_score - first_audit.overall_score,
                    "seo": last_audit.seo_score - first_audit.seo_score,
                    "accessibility": last_audit.accessibility_score - first_audit.accessibility_score,
                    "performance": last_audit.performance_score - first_audit.performance_score,
                }
                
                return {
                    "site_id": str(site_id),
                    "period_days": days,
                    "audit_count": len(audits),
                    "trends": trends,
                    "average_scores": {
                        "overall": round(avg_overall, 1),
                        "seo": round(avg_seo, 1),
                        "accessibility": round(avg_accessibility, 1),
                        "performance": round(avg_performance, 1),
                    },
                    "improvement": improvement,
                    "latest_audit": {
                        "id": str(last_audit.id),
                        "timestamp": last_audit.created_at.isoformat(),
                        "overall_score": last_audit.overall_score,
                    }
                }
        except Exception as e:
            logger.error(f"Error getting audit trends for site {site_id}: {str(e)}")
            return {
                "site_id": str(site_id),
                "period_days": days,
                "audit_count": 0,
                "error": str(e)
            }
    
    def get_issues_by_severity(
        self,
        site_id: uuid.UUID,
        severity: Optional[SeverityLevel] = None
    ) -> List[AuditIssue]:
        """
        Get audit issues for a site, optionally filtered by severity.
        
        Args:
            site_id: Site ID
            severity: Filter by severity level (optional)
            
        Returns:
            List of audit issues
        """
        try:
            with self._get_db_context() as db:
                query = db.query(AuditIssue).join(Audit).filter(
                    Audit.site_id == site_id
                )
                
                if severity:
                    query = query.filter(AuditIssue.severity == severity)
                
                issues = query.order_by(desc(AuditIssue.created_at)).all()
                return issues
        except Exception as e:
            logger.error(f"Error getting issues for site {site_id}: {str(e)}")
            return []
    
    def delete_audit(self, audit_id: uuid.UUID) -> bool:
        """
        Delete an audit and all its issues.
        
        Args:
            audit_id: Audit ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_db_context() as db:
                audit = db.query(Audit).filter(Audit.id == audit_id).first()
                if not audit:
                    return False
                
                db.delete(audit)
                if not self.db:
                    db.commit()
                logger.info(f"Deleted audit {audit_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting audit {audit_id}: {str(e)}")
            raise
