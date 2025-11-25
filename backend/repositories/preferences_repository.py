"""
User preferences repository for database operations.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session as DBSession
from contextlib import contextmanager
import uuid

from models.session import UserPreferences
from models.site import FrameworkTypeDB, DesignStyleTypeDB
from models.base import get_db
from utils.logging import logger


class PreferencesRepository:
    """Repository for user preferences database operations with transaction management."""
    
    def __init__(self, db: Optional[DBSession] = None):
        """
        Initialize repository.
        
        Args:
            db: Database session (optional, will create new if not provided)
        """
        self.db = db
    
    @contextmanager
    def _get_db_context(self):
        """
        Get database session context.
        Uses provided session or creates a new one with transaction management.
        """
        if self.db:
            # Use provided session, caller manages transaction
            yield self.db
        else:
            # Create new session with automatic transaction management
            with get_db() as db:
                yield db
    
    def create(
        self,
        session_id: uuid.UUID,
        default_color_scheme: Optional[str] = None,
        default_site_type: Optional[str] = None,
        favorite_features: Optional[List[str]] = None,
        design_style: Optional[str] = None,
        framework_preference: Optional[FrameworkTypeDB] = None,
        design_style_preference: Optional[DesignStyleTypeDB] = None,
    ) -> UserPreferences:
        """
        Create user preferences.
        
        Args:
            session_id: Session ID
            default_color_scheme: Default color scheme
            default_site_type: Default site type
            favorite_features: List of favorite features
            design_style: Design style preference (legacy string field)
            framework_preference: Framework preference enum
            design_style_preference: Design style preference enum
            
        Returns:
            Created preferences
        """
        try:
            with self._get_db_context() as db:
                preferences = UserPreferences(
                    session_id=session_id,
                    default_color_scheme=default_color_scheme,
                    default_site_type=default_site_type,
                    favorite_features=favorite_features or [],
                    design_style=design_style,
                    framework_preference=framework_preference,
                    design_style_preference=design_style_preference,
                )
                db.add(preferences)
                if not self.db:
                    db.commit()
                db.refresh(preferences)
                logger.info(f"Created preferences for session {session_id}")
                return preferences
        except Exception as e:
            logger.error(f"Error creating preferences: {str(e)}")
            raise
    
    def get_by_session_id(self, session_id: uuid.UUID) -> Optional[UserPreferences]:
        """
        Get preferences by session ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            User preferences or None if not found
        """
        try:
            with self._get_db_context() as db:
                preferences = db.query(UserPreferences).filter(
                    UserPreferences.session_id == session_id
                ).first()
                return preferences
        except Exception as e:
            logger.error(f"Error getting preferences for session {session_id}: {str(e)}")
            return None
    
    def update(
        self,
        session_id: uuid.UUID,
        default_color_scheme: Optional[str] = None,
        default_site_type: Optional[str] = None,
        favorite_features: Optional[List[str]] = None,
        design_style: Optional[str] = None,
        framework_preference: Optional[FrameworkTypeDB] = None,
        design_style_preference: Optional[DesignStyleTypeDB] = None,
    ) -> Optional[UserPreferences]:
        """
        Update user preferences.
        
        Args:
            session_id: Session ID
            default_color_scheme: Updated color scheme
            default_site_type: Updated site type
            favorite_features: Updated favorite features
            design_style: Updated design style (legacy string field)
            framework_preference: Updated framework preference enum
            design_style_preference: Updated design style preference enum
            
        Returns:
            Updated preferences or None if not found
        """
        try:
            with self._get_db_context() as db:
                preferences = db.query(UserPreferences).filter(
                    UserPreferences.session_id == session_id
                ).first()
                
                if not preferences:
                    # Create if doesn't exist
                    return self.create(
                        session_id=session_id,
                        default_color_scheme=default_color_scheme,
                        default_site_type=default_site_type,
                        favorite_features=favorite_features,
                        design_style=design_style,
                        framework_preference=framework_preference,
                        design_style_preference=design_style_preference,
                    )
                
                if default_color_scheme is not None:
                    preferences.default_color_scheme = default_color_scheme
                if default_site_type is not None:
                    preferences.default_site_type = default_site_type
                if favorite_features is not None:
                    preferences.favorite_features = favorite_features
                if design_style is not None:
                    preferences.design_style = design_style
                if framework_preference is not None:
                    preferences.framework_preference = framework_preference
                if design_style_preference is not None:
                    preferences.design_style_preference = design_style_preference
                
                preferences.updated_at = datetime.utcnow()
                if not self.db:
                    db.commit()
                db.refresh(preferences)
                logger.info(f"Updated preferences for session {session_id}")
                return preferences
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
            raise
    
    def delete(self, session_id: uuid.UUID) -> bool:
        """
        Delete user preferences.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_db_context() as db:
                preferences = db.query(UserPreferences).filter(
                    UserPreferences.session_id == session_id
                ).first()
                if not preferences:
                    return False
                
                db.delete(preferences)
                if not self.db:
                    db.commit()
                logger.info(f"Deleted preferences for session {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting preferences: {str(e)}")
            raise
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[UserPreferences]:
        """
        Get all preferences with pagination.
        
        Args:
            limit: Maximum number of preferences to return
            offset: Number of preferences to skip
            
        Returns:
            List of user preferences
        """
        try:
            with self._get_db_context() as db:
                preferences = db.query(UserPreferences).order_by(
                    UserPreferences.updated_at.desc()
                ).limit(limit).offset(offset).all()
                return preferences
        except Exception as e:
            logger.error(f"Error getting all preferences: {str(e)}")
            return []
