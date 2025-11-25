"""
Session repository for database operations.
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import and_
from contextlib import contextmanager
import uuid

from models.session import Session, UserPreferences
from models.base import get_db
from utils.logging import logger


class SessionRepository:
    """Repository for session database operations with transaction management."""
    
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
    
    def create(self, user_id: Optional[uuid.UUID] = None, preferences: Optional[dict] = None) -> Session:
        """
        Create a new session.
        
        Args:
            user_id: Optional user ID
            preferences: Optional user preferences
            
        Returns:
            Created session
        """
        try:
            with self._get_db_context() as db:
                session = Session(
                    user_id=user_id,
                    preferences=preferences or {},
                )
                db.add(session)
                if not self.db:
                    db.commit()
                db.refresh(session)
                logger.info(f"Created session {session.id}")
                return session
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            raise
    
    def get_by_id(self, session_id: uuid.UUID) -> Optional[Session]:
        """
        Get session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session or None if not found
        """
        try:
            with self._get_db_context() as db:
                session = db.query(Session).filter(Session.id == session_id).first()
                if session:
                    # Update last accessed time
                    session.last_accessed_at = datetime.utcnow()
                    if not self.db:
                        db.commit()
                return session
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {str(e)}")
            return None
    
    def update(self, session_id: uuid.UUID, preferences: Optional[dict] = None) -> Optional[Session]:
        """
        Update session.
        
        Args:
            session_id: Session ID
            preferences: Updated preferences
            
        Returns:
            Updated session or None if not found
        """
        try:
            with self._get_db_context() as db:
                session = db.query(Session).filter(Session.id == session_id).first()
                if not session:
                    return None
                
                if preferences is not None:
                    session.preferences = preferences
                
                session.last_accessed_at = datetime.utcnow()
                if not self.db:
                    db.commit()
                db.refresh(session)
                logger.info(f"Updated session {session_id}")
                return session
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            raise
    
    def delete(self, session_id: uuid.UUID) -> bool:
        """
        Delete session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._get_db_context() as db:
                session = db.query(Session).filter(Session.id == session_id).first()
                if not session:
                    return False
                
                db.delete(session)
                if not self.db:
                    db.commit()
                logger.info(f"Deleted session {session_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            raise
    
    def get_by_user_id(self, user_id: uuid.UUID) -> List[Session]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of sessions
        """
        try:
            with self._get_db_context() as db:
                sessions = db.query(Session).filter(Session.user_id == user_id).all()
                return sessions
        except Exception as e:
            logger.error(f"Error getting sessions for user {user_id}: {str(e)}")
            return []
    
    def cleanup_old_sessions(self, days: int = 90) -> int:
        """
        Delete sessions older than specified days.
        
        Args:
            days: Number of days to keep sessions
            
        Returns:
            Number of sessions deleted
        """
        try:
            with self._get_db_context() as db:
                cutoff_date = datetime.utcnow() - timedelta(days=days)
                deleted = db.query(Session).filter(
                    Session.last_accessed_at < cutoff_date
                ).delete()
                if not self.db:
                    db.commit()
                logger.info(f"Cleaned up {deleted} old sessions")
                return deleted
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {str(e)}")
            raise
    
    def get_all(self, limit: int = 100, offset: int = 0) -> List[Session]:
        """
        Get all sessions with pagination.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            List of sessions
        """
        try:
            with self._get_db_context() as db:
                sessions = db.query(Session).order_by(
                    Session.last_accessed_at.desc()
                ).limit(limit).offset(offset).all()
                return sessions
        except Exception as e:
            logger.error(f"Error getting all sessions: {str(e)}")
            return []
    
    def count(self) -> int:
        """
        Count total sessions.
        
        Returns:
            Total number of sessions
        """
        try:
            with self._get_db_context() as db:
                return db.query(Session).count()
        except Exception as e:
            logger.error(f"Error counting sessions: {str(e)}")
            return 0
