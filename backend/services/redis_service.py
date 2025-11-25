"""
Redis service for caching and session management.
"""
import redis
import json
from typing import Any, Optional
from datetime import timedelta

from utils.config import settings
from utils.logging import logger


class RedisService:
    """Redis service for caching and session management."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.client = redis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            decode_responses=True,
        )
        logger.info("Redis connection initialized")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            Value or None if not found
        """
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in Redis.
        
        Args:
            key: Redis key
            value: Value to store
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.
        
        Args:
            key: Redis key
            
        Returns:
            True if exists, False otherwise
        """
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {str(e)}")
            return False
    
    def set_session(self, session_id: str, data: dict) -> bool:
        """
        Store session data.
        
        Args:
            session_id: Session ID
            data: Session data
            
        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        ttl = settings.SESSION_TTL_HOURS * 3600
        return self.set(key, data, ttl)
    
    def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None
        """
        key = f"session:{session_id}"
        return self.get(key)
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete session data.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        key = f"session:{session_id}"
        return self.delete(key)
    
    def set_workflow_state(self, workflow_id: str, state: dict) -> bool:
        """
        Store workflow state.
        
        Args:
            workflow_id: Workflow ID
            state: Workflow state
            
        Returns:
            True if successful, False otherwise
        """
        key = f"workflow:{workflow_id}:state"
        ttl = 3600  # 1 hour
        return self.set(key, state, ttl)
    
    def get_workflow_state(self, workflow_id: str) -> Optional[dict]:
        """
        Get workflow state.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow state or None
        """
        key = f"workflow:{workflow_id}:state"
        return self.get(key)
    
    def set_agent_metrics(self, agent_name: str, metrics: dict) -> bool:
        """
        Store agent metrics.
        
        Args:
            agent_name: Agent name
            metrics: Agent metrics
            
        Returns:
            True if successful, False otherwise
        """
        key = f"agent:{agent_name}:metrics"
        ttl = 300  # 5 minutes
        return self.set(key, metrics, ttl)
    
    def get_agent_metrics(self, agent_name: str) -> Optional[dict]:
        """
        Get agent metrics.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Agent metrics or None
        """
        key = f"agent:{agent_name}:metrics"
        return self.get(key)
    
    def set_site_cache(self, site_id: str, data: dict) -> bool:
        """
        Cache site data.
        
        Args:
            site_id: Site ID
            data: Site data
            
        Returns:
            True if successful, False otherwise
        """
        key = f"site:{site_id}:latest"
        ttl = 3600  # 1 hour
        return self.set(key, data, ttl)
    
    def get_site_cache(self, site_id: str) -> Optional[dict]:
        """
        Get cached site data.
        
        Args:
            site_id: Site ID
            
        Returns:
            Site data or None
        """
        key = f"site:{site_id}:latest"
        return self.get(key)
    
    def ping(self) -> bool:
        """
        Check Redis connection.
        
        Returns:
            True if connected, False otherwise
        """
        try:
            return self.client.ping()
        except Exception as e:
            logger.error(f"Redis PING error: {str(e)}")
            return False


# Global Redis service instance
redis_service = RedisService()
