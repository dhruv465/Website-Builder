"""
Session and user preferences models.
"""
from sqlalchemy import Column, String, DateTime, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from models.base import Base
from models.site import FrameworkTypeDB, DesignStyleTypeDB


class Session(Base):
    """User session model."""
    
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_accessed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    preferences = Column(JSON, default=dict, nullable=False)
    
    def __repr__(self):
        return f"<Session(id={self.id}, created_at={self.created_at})>"


class UserPreferences(Base):
    """User preferences model (alternative to JSON in Session)."""
    
    __tablename__ = "user_preferences"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    default_color_scheme = Column(String(100), nullable=True)
    default_site_type = Column(String(100), nullable=True)
    favorite_features = Column(JSON, default=list, nullable=False)
    design_style = Column(String(100), nullable=True)
    framework_preference = Column(Enum(FrameworkTypeDB, name='framework_type'), nullable=True)
    design_style_preference = Column(Enum(DesignStyleTypeDB, name='design_style_type'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<UserPreferences(id={self.id}, session_id={self.session_id})>"
