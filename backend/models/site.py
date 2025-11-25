"""
Site and site version models.
"""
from sqlalchemy import Column, String, DateTime, Integer, Float, Text, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from models.base import Base


class FrameworkTypeDB(str, enum.Enum):
    """Framework types enum for database."""
    VANILLA = "vanilla"
    REACT = "react"
    VUE = "vue"
    NEXTJS = "nextjs"
    SVELTE = "svelte"


class DesignStyleTypeDB(str, enum.Enum):
    """Design style types enum for database."""
    BOLD_MINIMALISM = "bold_minimalism"
    BRUTALISM = "brutalism"
    FLAT_MINIMALIST = "flat_minimalist"
    ANTI_DESIGN = "anti_design"
    VIBRANT_BLOCKS = "vibrant_blocks"
    ORGANIC_FLUID = "organic_fluid"
    RETRO_NOSTALGIC = "retro_nostalgic"
    EXPERIMENTAL = "experimental"


class Site(Base):
    """Site model."""
    
    __tablename__ = "sites"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    framework = Column(Enum(FrameworkTypeDB, name='framework_type'), nullable=True)
    design_style = Column(Enum(DesignStyleTypeDB, name='design_style_type'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    versions = relationship("SiteVersion", back_populates="site", cascade="all, delete-orphan")
    audits = relationship("Audit", back_populates="site", cascade="all, delete-orphan")
    deployments = relationship("Deployment", back_populates="site", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="site", cascade="all, delete-orphan")
    forms = relationship("Form", back_populates="site", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Site(id={self.id}, name={self.name})>"


class SiteVersion(Base):
    """Site version model."""
    
    __tablename__ = "site_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    code = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=True)
    changes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    audit_score = Column(Float, nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="versions")
    
    def __repr__(self):
        return f"<SiteVersion(id={self.id}, site_id={self.site_id}, version={self.version_number})>"


class FrameworkChange(Base):
    """Framework change tracking model."""
    
    __tablename__ = "framework_changes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), ForeignKey("sites.id"), nullable=False, index=True)
    from_framework = Column(Enum(FrameworkTypeDB, name='framework_type'), nullable=True)
    to_framework = Column(Enum(FrameworkTypeDB, name='framework_type'), nullable=False)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<FrameworkChange(id={self.id}, site_id={self.site_id}, from={self.from_framework}, to={self.to_framework})>"
