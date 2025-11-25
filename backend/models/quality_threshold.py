"""
Quality threshold model for automatic improvement workflow.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.sql import func
from models.base import Base


class QualityThreshold(Base):
    """Quality threshold configuration for automatic improvements."""
    
    __tablename__ = "quality_thresholds"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    seo_min_score = Column(Integer, nullable=False, default=70)
    accessibility_min_score = Column(Integer, nullable=False, default=80)
    performance_min_score = Column(Integer, nullable=False, default=75)
    overall_min_score = Column(Integer, nullable=False, default=75)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<QualityThreshold(name='{self.name}', seo={self.seo_min_score}, a11y={self.accessibility_min_score}, perf={self.performance_min_score})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "seo_min_score": self.seo_min_score,
            "accessibility_min_score": self.accessibility_min_score,
            "performance_min_score": self.performance_min_score,
            "overall_min_score": self.overall_min_score,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def check_thresholds(self, audit_result: dict) -> dict:
        """
        Check if audit scores meet thresholds.
        
        Args:
            audit_result: Audit result dictionary with scores
            
        Returns:
            Dictionary with threshold check results
        """
        seo_score = audit_result.get("seo", {}).get("score", 0)
        accessibility_score = audit_result.get("accessibility", {}).get("score", 0)
        performance_score = audit_result.get("performance", {}).get("score", 0)
        overall_score = audit_result.get("overall_score", 0)
        
        return {
            "meets_thresholds": (
                seo_score >= self.seo_min_score and
                accessibility_score >= self.accessibility_min_score and
                performance_score >= self.performance_min_score and
                overall_score >= self.overall_min_score
            ),
            "seo_pass": seo_score >= self.seo_min_score,
            "accessibility_pass": accessibility_score >= self.accessibility_min_score,
            "performance_pass": performance_score >= self.performance_min_score,
            "overall_pass": overall_score >= self.overall_min_score,
            "seo_gap": max(0, self.seo_min_score - seo_score),
            "accessibility_gap": max(0, self.accessibility_min_score - accessibility_score),
            "performance_gap": max(0, self.performance_min_score - performance_score),
            "overall_gap": max(0, self.overall_min_score - overall_score),
        }
