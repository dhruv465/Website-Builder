"""
Repository for quality threshold operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
import uuid

from models.quality_threshold import QualityThreshold
from utils.logging import logger


class QualityThresholdRepository:
    """Repository for quality threshold database operations."""
    
    def __init__(self, db_session: Session):
        """
        Initialize repository.
        
        Args:
            db_session: Database session
        """
        self.db = db_session
    
    def create_default_threshold(self) -> QualityThreshold:
        """
        Create default quality threshold configuration.
        
        Returns:
            Created QualityThreshold instance
        """
        threshold = QualityThreshold(
            id=str(uuid.uuid4()),
            name="default",
            seo_min_score=70,
            accessibility_min_score=80,
            performance_min_score=75,
            overall_min_score=75,
            enabled=True,
        )
        
        self.db.add(threshold)
        self.db.commit()
        self.db.refresh(threshold)
        
        logger.info(f"Created default quality threshold: {threshold.id}")
        return threshold
    
    def get_by_name(self, name: str) -> Optional[QualityThreshold]:
        """
        Get quality threshold by name.
        
        Args:
            name: Threshold name
            
        Returns:
            QualityThreshold instance or None
        """
        return self.db.query(QualityThreshold).filter(
            QualityThreshold.name == name
        ).first()
    
    def get_by_id(self, threshold_id: str) -> Optional[QualityThreshold]:
        """
        Get quality threshold by ID.
        
        Args:
            threshold_id: Threshold ID
            
        Returns:
            QualityThreshold instance or None
        """
        return self.db.query(QualityThreshold).filter(
            QualityThreshold.id == threshold_id
        ).first()
    
    def get_active_threshold(self) -> Optional[QualityThreshold]:
        """
        Get the active (enabled) quality threshold.
        Defaults to 'default' threshold if multiple are enabled.
        
        Returns:
            QualityThreshold instance or None
        """
        # Try to get default threshold first
        threshold = self.get_by_name("default")
        if threshold and threshold.enabled:
            return threshold
        
        # Otherwise get any enabled threshold
        threshold = self.db.query(QualityThreshold).filter(
            QualityThreshold.enabled == True
        ).first()
        
        # If no threshold exists, create default
        if not threshold:
            threshold = self.create_default_threshold()
        
        return threshold
    
    def update_threshold(
        self,
        threshold_id: str,
        seo_min_score: Optional[int] = None,
        accessibility_min_score: Optional[int] = None,
        performance_min_score: Optional[int] = None,
        overall_min_score: Optional[int] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[QualityThreshold]:
        """
        Update quality threshold.
        
        Args:
            threshold_id: Threshold ID
            seo_min_score: Minimum SEO score
            accessibility_min_score: Minimum accessibility score
            performance_min_score: Minimum performance score
            overall_min_score: Minimum overall score
            enabled: Whether threshold is enabled
            
        Returns:
            Updated QualityThreshold instance or None
        """
        threshold = self.get_by_id(threshold_id)
        if not threshold:
            return None
        
        if seo_min_score is not None:
            threshold.seo_min_score = seo_min_score
        if accessibility_min_score is not None:
            threshold.accessibility_min_score = accessibility_min_score
        if performance_min_score is not None:
            threshold.performance_min_score = performance_min_score
        if overall_min_score is not None:
            threshold.overall_min_score = overall_min_score
        if enabled is not None:
            threshold.enabled = enabled
        
        self.db.commit()
        self.db.refresh(threshold)
        
        logger.info(f"Updated quality threshold: {threshold_id}")
        return threshold
    
    def list_all(self) -> List[QualityThreshold]:
        """
        List all quality thresholds.
        
        Returns:
            List of QualityThreshold instances
        """
        return self.db.query(QualityThreshold).all()
    
    def delete(self, threshold_id: str) -> bool:
        """
        Delete quality threshold.
        
        Args:
            threshold_id: Threshold ID
            
        Returns:
            True if deleted, False otherwise
        """
        threshold = self.get_by_id(threshold_id)
        if not threshold:
            return False
        
        # Don't allow deleting default threshold
        if threshold.name == "default":
            logger.warning("Cannot delete default quality threshold")
            return False
        
        self.db.delete(threshold)
        self.db.commit()
        
        logger.info(f"Deleted quality threshold: {threshold_id}")
        return True
