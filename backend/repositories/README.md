# Repository Layer Documentation

## Overview

The repository layer provides a clean abstraction for database operations with built-in transaction management and connection pooling. Each repository supports both standalone usage and dependency injection patterns.

## Features

- **Connection Pooling**: Automatic connection pool management with configurable size and overflow
- **Transaction Management**: Automatic commit/rollback with context managers
- **Flexible Usage**: Support for both standalone and dependency injection patterns
- **Error Handling**: Comprehensive error logging and exception handling
- **Type Safety**: Full type hints for better IDE support

## Connection Pooling

Connection pooling is configured in `models/base.py`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,              # Number of connections to maintain
    max_overflow=10,           # Additional connections when pool is full
    pool_pre_ping=True,        # Verify connections before using
    pool_recycle=3600,         # Recycle connections after 1 hour
    poolclass=pool.QueuePool,  # Use QueuePool for connection pooling
)
```

### Monitoring Connection Pool

```python
from models.base import get_pool_status

# Get current pool statistics
status = get_pool_status()
print(f"Pool size: {status['size']}")
print(f"Checked in: {status['checked_in']}")
print(f"Checked out: {status['checked_out']}")
print(f"Overflow: {status['overflow']}")
```

## Transaction Management

### Automatic Transaction Management (Standalone Usage)

When using repositories without providing a database session, transactions are managed automatically:

```python
from repositories import SessionRepository

# Create repository without db session
repo = SessionRepository()

# Transaction is automatically committed on success
session = repo.create(user_id=user_id, preferences={"theme": "dark"})

# Transaction is automatically rolled back on error
try:
    repo.update(session_id, preferences={"invalid": "data"})
except Exception as e:
    # Rollback already happened automatically
    print(f"Error: {e}")
```

### Manual Transaction Management (Dependency Injection)

When providing a database session, you control the transaction:

```python
from models.base import get_db
from repositories import SessionRepository, SiteRepository

# Manual transaction control
with get_db() as db:
    session_repo = SessionRepository(db=db)
    site_repo = SiteRepository(db=db)
    
    # Create session
    session = session_repo.create(user_id=user_id)
    
    # Create site in same transaction
    site = site_repo.create_site(session_id=session.id, name="My Site")
    
    # Both operations committed together when context exits
    # Or rolled back together if any error occurs
```

### FastAPI Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.orm import Session as DBSession
from models.base import get_db_session
from repositories import SessionRepository

@app.post("/sessions")
def create_session(
    user_id: str,
    db: DBSession = Depends(get_db_session)
):
    repo = SessionRepository(db=db)
    session = repo.create(user_id=uuid.UUID(user_id))
    return session
```

## Repository Usage Examples

### SessionRepository

```python
from repositories import SessionRepository
import uuid

# Create repository
repo = SessionRepository()

# Create a new session
session = repo.create(
    user_id=uuid.uuid4(),
    preferences={"theme": "dark", "language": "en"}
)

# Get session by ID (updates last_accessed_at)
session = repo.get_by_id(session.id)

# Update session preferences
session = repo.update(
    session_id=session.id,
    preferences={"theme": "light", "language": "es"}
)

# Get all sessions for a user
sessions = repo.get_by_user_id(user_id)

# Get all sessions with pagination
sessions = repo.get_all(limit=50, offset=0)

# Count total sessions
total = repo.count()

# Cleanup old sessions (older than 90 days)
deleted_count = repo.cleanup_old_sessions(days=90)

# Delete a session
success = repo.delete(session.id)
```

### SiteRepository

```python
from repositories import SiteRepository
import uuid

# Create repository
repo = SiteRepository()

# Create a new site
site = repo.create_site(
    session_id=session_id,
    name="My Portfolio"
)

# Get site by ID (with all relationships loaded)
site = repo.get_site_by_id(site.id)

# Get all sites for a session
sites = repo.get_sites_by_session(session_id)

# Update site
site = repo.update_site(site_id=site.id, name="Updated Name")

# Create a new version
version = repo.create_version(
    site_id=site.id,
    code="<html>...</html>",
    requirements={"type": "portfolio", "features": ["contact"]},
    changes="Added contact form"
)

# Get version by ID
version = repo.get_version_by_id(version.id)

# Get all versions for a site
versions = repo.get_versions_by_site(site.id)

# Get latest version
latest = repo.get_latest_version(site.id)

# Update version audit score
version = repo.update_version_audit_score(
    version_id=version.id,
    audit_score=85.5
)

# Get all audits for a site
audits = repo.get_audits_by_site(site.id)

# Get all deployments for a site
deployments = repo.get_deployments_by_site(site.id)

# Delete site (cascades to versions, audits, deployments)
success = repo.delete_site(site.id)
```

### PreferencesRepository

```python
from repositories import PreferencesRepository
import uuid

# Create repository
repo = PreferencesRepository()

# Create preferences
preferences = repo.create(
    session_id=session_id,
    default_color_scheme="blue",
    default_site_type="portfolio",
    favorite_features=["contact", "gallery"],
    design_style="modern"
)

# Get preferences by session ID
preferences = repo.get_by_session_id(session_id)

# Update preferences (creates if doesn't exist)
preferences = repo.update(
    session_id=session_id,
    default_color_scheme="green",
    favorite_features=["contact", "gallery", "blog"]
)

# Get all preferences with pagination
all_prefs = repo.get_all(limit=100, offset=0)

# Delete preferences
success = repo.delete(session_id)
```

## Multi-Repository Transactions

When you need to perform operations across multiple repositories in a single transaction:

```python
from models.base import get_db
from repositories import SessionRepository, SiteRepository, PreferencesRepository

with get_db() as db:
    session_repo = SessionRepository(db=db)
    site_repo = SiteRepository(db=db)
    prefs_repo = PreferencesRepository(db=db)
    
    # All operations in same transaction
    session = session_repo.create(user_id=user_id)
    
    prefs = prefs_repo.create(
        session_id=session.id,
        default_site_type="portfolio"
    )
    
    site = site_repo.create_site(
        session_id=session.id,
        name="My First Site"
    )
    
    version = site_repo.create_version(
        site_id=site.id,
        code="<html>...</html>"
    )
    
    # All committed together when context exits
    # Or all rolled back if any operation fails
```

## Error Handling

All repository methods include comprehensive error handling:

```python
from repositories import SessionRepository

repo = SessionRepository()

try:
    session = repo.create(user_id=user_id)
except Exception as e:
    # Error is logged automatically
    # Transaction is rolled back automatically
    print(f"Failed to create session: {e}")
```

## Best Practices

1. **Use standalone mode for simple operations**: When you only need one repository operation, let it manage its own transaction.

2. **Use dependency injection for complex workflows**: When you need multiple operations to succeed or fail together, provide a shared database session.

3. **Let the context manager handle commits**: Don't manually call `db.commit()` when using `get_db()` context manager.

4. **Use connection pooling wisely**: Configure pool size based on your application's concurrency needs.

5. **Monitor pool status**: Regularly check pool statistics to ensure you're not exhausting connections.

6. **Clean up old data**: Use `cleanup_old_sessions()` in a scheduled task to maintain database size.

## Configuration

Connection pool settings are configured in `utils/config.py`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
```

Set these via environment variables:

```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

## Testing

When testing repositories, provide a test database session:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from repositories import SessionRepository

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_session(db_session):
    repo = SessionRepository(db=db_session)
    session = repo.create(user_id=uuid.uuid4())
    assert session.id is not None
```
