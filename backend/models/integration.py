"""
Integration database model for storing workflow integrations.
"""
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from models.base import Base


class Integration(Base):
    """
    Integration model for storing workflow integration configurations.
    
    Stores information about third-party service integrations added to sites,
    including payment processors, booking systems, and contact forms.
    """
    __tablename__ = "integrations"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False, index=True)
    
    # Integration details
    integration_type = Column(String(50), nullable=False)  # payment, booking, contact
    provider = Column(String(100), nullable=False)  # stripe, calendly, formspree, etc.
    
    # Integration code
    html_snippet = Column(Text, nullable=False)
    javascript_snippet = Column(Text, nullable=True)
    css_snippet = Column(Text, nullable=True)
    dependencies = Column(JSON, nullable=True)  # List of CDN links
    
    # Configuration
    config = Column(JSON, nullable=True)  # Provider-specific configuration
    
    # Setup information
    setup_instructions = Column(JSON, nullable=True)  # Setup steps and instructions
    
    # Security validation
    is_secure = Column(Boolean, default=True)
    security_issues = Column(JSON, nullable=True)  # List of security issues
    security_warnings = Column(JSON, nullable=True)  # List of security warnings
    security_recommendations = Column(JSON, nullable=True)  # List of recommendations
    
    # Metadata
    confidence_score = Column(String(10), nullable=True)  # Confidence score as string
    is_active = Column(Boolean, default=True)  # Whether integration is currently active
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    site = relationship("Site", back_populates="integrations")
    
    def __repr__(self):
        """String representation."""
        return f"<Integration(id={self.id}, type={self.integration_type}, provider={self.provider})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "site_id": str(self.site_id),
            "integration_type": self.integration_type,
            "provider": self.provider,
            "html_snippet": self.html_snippet,
            "javascript_snippet": self.javascript_snippet,
            "css_snippet": self.css_snippet,
            "dependencies": self.dependencies,
            "config": self.config,
            "setup_instructions": self.setup_instructions,
            "is_secure": self.is_secure,
            "security_issues": self.security_issues,
            "security_warnings": self.security_warnings,
            "security_recommendations": self.security_recommendations,
            "confidence_score": self.confidence_score,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
