"""
Improvement cycle model for tracking automatic improvements.
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from models.base import Base


class ImprovementCycle(Base):
    """Track automatic improvement cycles."""
    
    __tablename__ = "improvement_cycles"
    
    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False, index=True)
    session_id = Column(String, nullable=False, index=True)
    site_id = Column(String, nullable=True, index=True)
    cycle_number = Column(Integer, nullable=False)
    
    # Scores before improvement
    initial_seo_score = Column(Integer, nullable=False)
    initial_accessibility_score = Column(Integer, nullable=False)
    initial_performance_score = Column(Integer, nullable=False)
    initial_overall_score = Column(Integer, nullable=False)
    
    # Scores after improvement
    final_seo_score = Column(Integer, nullable=True)
    final_accessibility_score = Column(Integer, nullable=True)
    final_performance_score = Column(Integer, nullable=True)
    final_overall_score = Column(Integer, nullable=True)
    
    # Improvement details
    issues_addressed = Column(JSON, nullable=True)
    improvement_instructions = Column(String, nullable=True)
    success = Column(Integer, nullable=True)  # 1 for success, 0 for failure, NULL for in progress
    error_message = Column(String, nullable=True)
    
    # Timing
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<ImprovementCycle(workflow_id='{self.workflow_id}', cycle={self.cycle_number}, success={self.success})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "session_id": self.session_id,
            "site_id": self.site_id,
            "cycle_number": self.cycle_number,
            "initial_scores": {
                "seo": self.initial_seo_score,
                "accessibility": self.initial_accessibility_score,
                "performance": self.initial_performance_score,
                "overall": self.initial_overall_score,
            },
            "final_scores": {
                "seo": self.final_seo_score,
                "accessibility": self.final_accessibility_score,
                "performance": self.final_performance_score,
                "overall": self.final_overall_score,
            } if self.final_overall_score is not None else None,
            "improvement": {
                "seo": self.final_seo_score - self.initial_seo_score if self.final_seo_score else None,
                "accessibility": self.final_accessibility_score - self.initial_accessibility_score if self.final_accessibility_score else None,
                "performance": self.final_performance_score - self.initial_performance_score if self.final_performance_score else None,
                "overall": self.final_overall_score - self.initial_overall_score if self.final_overall_score else None,
            } if self.final_overall_score is not None else None,
            "issues_addressed": self.issues_addressed,
            "improvement_instructions": self.improvement_instructions,
            "success": bool(self.success) if self.success is not None else None,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
        }
