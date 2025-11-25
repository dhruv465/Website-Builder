"""
Deployment model.
"""
from sqlalchemy import Column, String, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.base import Base


class Deployment(Base):
    """Deployment model."""
    
    __tablename__ = "deployments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False, index=True)
    site_version_id = Column(UUID(as_uuid=True), ForeignKey("site_versions.id"), nullable=True, index=True)
    url = Column(String(512), nullable=False)
    deployment_id = Column(String(255), nullable=False)
    project_id = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    framework = Column(String(50), nullable=False, default="vanilla")
    build_config = Column(JSON, nullable=True)
    build_time = Column(Integer, nullable=True)  # in milliseconds
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    site = relationship("Site", back_populates="deployments")
    
    def __repr__(self):
        return f"<Deployment(id={self.id}, url={self.url}, framework={self.framework}, status={self.status})>"
