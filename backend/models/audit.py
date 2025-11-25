"""
Audit and audit issue models.
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from models.base import Base


class SeverityLevel(str, enum.Enum):
    """Severity levels for audit issues."""
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class Audit(Base):
    """Audit model."""
    
    __tablename__ = "audits"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False, index=True)
    site_version_id = Column(UUID(as_uuid=True), ForeignKey("site_versions.id"), nullable=True, index=True)
    seo_score = Column(Integer, nullable=False)
    accessibility_score = Column(Integer, nullable=False)
    performance_score = Column(Integer, nullable=False)
    overall_score = Column(Integer, nullable=False)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    site = relationship("Site", back_populates="audits")
    issues = relationship("AuditIssue", back_populates="audit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Audit(id={self.id}, site_id={self.site_id}, overall_score={self.overall_score})>"


class AuditIssue(Base):
    """Audit issue model."""
    
    __tablename__ = "audit_issues"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    audit_id = Column(UUID(as_uuid=True), ForeignKey("audits.id"), nullable=False, index=True)
    category = Column(String(50), nullable=False)  # seo, accessibility, performance
    severity = Column(Enum(SeverityLevel), nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String(500), nullable=True)
    fix_suggestion = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    audit = relationship("Audit", back_populates="issues")
    
    def __repr__(self):
        return f"<AuditIssue(id={self.id}, severity={self.severity}, category={self.category})>"
