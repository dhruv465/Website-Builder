"""
Models for Form Builder and Submissions.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from models.base import Base

class Form(Base):
    """Form configuration model."""
    __tablename__ = "forms"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    site_id = Column(String, ForeignKey("sites.id"), nullable=False)
    name = Column(String, nullable=False)
    fields = Column(JSON, nullable=False)  # List of form fields configuration
    settings = Column(JSON, nullable=False)  # Settings like email_to, success_message, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    site = relationship("Site", back_populates="forms")
    submissions = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")

class FormSubmission(Base):
    """Form submission data model."""
    __tablename__ = "form_submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    form_id = Column(String, ForeignKey("forms.id"), nullable=False)
    data = Column(JSON, nullable=False)  # The submitted data
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    spam_score = Column(Float, default=0.0)
    is_spam = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    form = relationship("Form", back_populates="submissions")
