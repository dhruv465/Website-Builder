"""
Base database model and session management.
"""
from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as DBSession
from contextlib import contextmanager
from typing import Generator

from utils.config import settings
from utils.logging import logger

# Create database engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False,  # Set to True for SQL logging
    poolclass=pool.QueuePool,  # Use QueuePool for connection pooling
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


# Connection pool event listeners for monitoring
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log when a new connection is created."""
    logger.debug("Database connection established")


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log when a connection is checked out from the pool."""
    logger.debug("Database connection checked out from pool")


@event.listens_for(engine, "checkin")
def receive_checkin(dbapi_conn, connection_record):
    """Log when a connection is returned to the pool."""
    logger.debug("Database connection returned to pool")


@contextmanager
def get_db() -> Generator[DBSession, None, None]:
    """
    Get database session context manager with automatic transaction management.
    
    Usage:
        with get_db() as db:
            # Use db session
            # Automatically commits on success, rolls back on exception
            pass
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database transaction rolled back: {str(e)}")
        raise
    finally:
        db.close()


def get_db_session() -> Generator[DBSession, None, None]:
    """
    Get database session for dependency injection in FastAPI.
    
    Usage in FastAPI:
        @app.get("/")
        def endpoint(db: DBSession = Depends(get_db_session)):
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_pool_status() -> dict:
    """
    Get current connection pool status for monitoring.
    
    Returns:
        Dictionary with pool statistics
    """
    pool_obj = engine.pool
    return {
        "size": pool_obj.size(),
        "checked_in": pool_obj.checkedin(),
        "checked_out": pool_obj.checkedout(),
        "overflow": pool_obj.overflow(),
        "total_connections": pool_obj.size() + pool_obj.overflow(),
    }
