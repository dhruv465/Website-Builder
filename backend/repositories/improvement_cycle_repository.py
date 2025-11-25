"""
Repository for improvement cycle operations.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from models.improvement_cycle import ImprovementCycle
from utils.logging import logger


class ImprovementCycleRepository:
    """Repository for improvement cycle database operations."""
    
    def __init__(self, db_session: Session):
        """
        Initialize repository.
        
        Args:
            db_session: Database session
        """
        self.db = db_session
    
    def create_cycle(
        self,
        workflow_id: str,
        session_id: str,
        cycle_number: int,
        initial_seo_score: int,
        initial_accessibility_score: int,
        initial_performance_score: int,
        initial_overall_score: int,
        site_id: Optional[str] = None,
        improvement_instructions: Optional[str] = None,
        issues_addressed: Optional[dict] = None,
    ) -> ImprovementCycle:
        """
        Create a new improvement cycle record.
        
        Args:
            workflow_id: Workflow ID
            session_id: Session ID
            cycle_number: Cycle number (1, 2, etc.)
            initial_seo_score: Initial SEO score
            initial_accessibility_score: Initial accessibility score
            initial_performance_score: Initial performance score
            initial_overall_score: Initial overall score
            site_id: Optional site ID
            improvement_instructions: Instructions for improvement
            issues_addressed: Issues being addressed
            
        Returns:
            Created ImprovementCycle instance
        """
        cycle = ImprovementCycle(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            session_id=session_id,
            site_id=site_id,
            cycle_number=cycle_number,
            initial_seo_score=initial_seo_score,
            initial_accessibility_score=initial_accessibility_score,
            initial_performance_score=initial_performance_score,
            initial_overall_score=initial_overall_score,
            improvement_instructions=improvement_instructions,
            issues_addressed=issues_addressed,
        )
        
        self.db.add(cycle)
        self.db.commit()
        self.db.refresh(cycle)
        
        logger.info(f"Created improvement cycle {cycle_number} for workflow {workflow_id}")
        return cycle
    
    def complete_cycle(
        self,
        cycle_id: str,
        final_seo_score: int,
        final_accessibility_score: int,
        final_performance_score: int,
        final_overall_score: int,
        success: bool,
        error_message: Optional[str] = None,
    ) -> Optional[ImprovementCycle]:
        """
        Mark improvement cycle as complete.
        
        Args:
            cycle_id: Cycle ID
            final_seo_score: Final SEO score
            final_accessibility_score: Final accessibility score
            final_performance_score: Final performance score
            final_overall_score: Final overall score
            success: Whether improvement was successful
            error_message: Optional error message
            
        Returns:
            Updated ImprovementCycle instance or None
        """
        cycle = self.get_by_id(cycle_id)
        if not cycle:
            return None
        
        cycle.final_seo_score = final_seo_score
        cycle.final_accessibility_score = final_accessibility_score
        cycle.final_performance_score = final_performance_score
        cycle.final_overall_score = final_overall_score
        cycle.success = 1 if success else 0
        cycle.error_message = error_message
        cycle.completed_at = datetime.utcnow()
        
        if cycle.started_at:
            duration = (cycle.completed_at - cycle.started_at).total_seconds()
            cycle.duration_seconds = int(duration)
        
        self.db.commit()
        self.db.refresh(cycle)
        
        logger.info(f"Completed improvement cycle {cycle.id}: success={success}")
        return cycle
    
    def get_by_id(self, cycle_id: str) -> Optional[ImprovementCycle]:
        """
        Get improvement cycle by ID.
        
        Args:
            cycle_id: Cycle ID
            
        Returns:
            ImprovementCycle instance or None
        """
        return self.db.query(ImprovementCycle).filter(
            ImprovementCycle.id == cycle_id
        ).first()
    
    def get_by_workflow(self, workflow_id: str) -> List[ImprovementCycle]:
        """
        Get all improvement cycles for a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            List of ImprovementCycle instances
        """
        return self.db.query(ImprovementCycle).filter(
            ImprovementCycle.workflow_id == workflow_id
        ).order_by(ImprovementCycle.cycle_number).all()
    
    def get_by_session(self, session_id: str) -> List[ImprovementCycle]:
        """
        Get all improvement cycles for a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of ImprovementCycle instances
        """
        return self.db.query(ImprovementCycle).filter(
            ImprovementCycle.session_id == session_id
        ).order_by(ImprovementCycle.started_at.desc()).all()
    
    def get_by_site(self, site_id: str) -> List[ImprovementCycle]:
        """
        Get all improvement cycles for a site.
        
        Args:
            site_id: Site ID
            
        Returns:
            List of ImprovementCycle instances
        """
        return self.db.query(ImprovementCycle).filter(
            ImprovementCycle.site_id == site_id
        ).order_by(ImprovementCycle.started_at.desc()).all()
    
    def get_cycle_count(self, workflow_id: str) -> int:
        """
        Get the number of improvement cycles for a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Number of cycles
        """
        return self.db.query(ImprovementCycle).filter(
            ImprovementCycle.workflow_id == workflow_id
        ).count()
    
    def get_latest_cycle(self, workflow_id: str) -> Optional[ImprovementCycle]:
        """
        Get the latest improvement cycle for a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Latest ImprovementCycle instance or None
        """
        return self.db.query(ImprovementCycle).filter(
            ImprovementCycle.workflow_id == workflow_id
        ).order_by(ImprovementCycle.cycle_number.desc()).first()
