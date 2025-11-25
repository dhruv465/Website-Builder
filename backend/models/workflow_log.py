"""
Workflow log model.
"""
from sqlalchemy import Column, String, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from models.base import Base


class WorkflowLog(Base):
    """Workflow log model."""
    
    __tablename__ = "workflow_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    agent_name = Column(String(100), nullable=True)
    level = Column(String(20), nullable=False)  # info, warning, error
    message = Column(Text, nullable=False)
    log_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<WorkflowLog(id={self.id}, workflow_id={self.workflow_id}, level={self.level})>"
