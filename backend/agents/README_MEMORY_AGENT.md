# Memory Agent Implementation

## Overview
The Memory Agent manages session state, user preferences, and site data persistence for the Smart Website Builder platform.

## Components Implemented

### 1. Repository Layer (`backend/repositories/`)
- **SessionRepository**: CRUD operations for user sessions
  - Create, read, update, delete sessions
  - Cleanup old sessions (90-day retention)
  - Pagination support
  
- **SiteRepository**: Site and version management
  - Create and manage sites
  - Version history tracking
  - Audit and deployment record retrieval
  - Latest version caching
  
- **PreferencesRepository**: User preferences management
  - Store and update user preferences
  - Default color schemes, site types, favorite features
  - Design style preferences

### 2. Memory Agent (`backend/agents/memory_agent.py`)
Implements the following operations:
- **Save Session**: Create or update session data with Redis caching
- **Load Session**: Retrieve session from cache or database
- **Save Site**: Store site data with version history
- **Load Site**: Retrieve site with all versions, audits, and deployments
- **Update Preferences**: Manage user preferences with caching
- **Cleanup**: Remove old sessions (scheduled task)
- **Export Session**: Serialize session data to JSON with gzip compression
- **Import Session**: Restore session from backup

### 3. API Endpoints (`backend/api/sessions.py`)
- `GET /sessions/{session_id}` - Load session data
- `POST /sessions` - Create new session
- `PUT /sessions/{session_id}` - Update session
- `PUT /sessions/{session_id}/preferences` - Update preferences
- `GET /sessions/sites/{site_id}` - Get site details
- `GET /sessions/sites/{site_id}/versions` - Get version history
- `POST /sessions/export` - Export session data
- `POST /sessions/import` - Import session data

### 4. Scheduled Tasks (`backend/services/tasks.py`)
- **cleanup_old_sessions**: Celery Beat task that runs daily at 2 AM UTC
- Automatically removes sessions older than 90 days
- Configured in `backend/services/celery_app.py`

## Features

### Caching Strategy
- Redis caching for active sessions (24-hour TTL)
- Site data caching (1-hour TTL)
- Automatic cache invalidation on updates

### Data Compression
- Gzip compression for large code strings in export
- Base64 encoding for transport
- Configurable compression option

### Version History
- Automatic version numbering
- Track changes and requirements per version
- Audit score tracking per version

### Error Handling
- Comprehensive error types (validation, storage, network)
- Retry logic for transient failures
- User-friendly error messages

## Usage Examples

### Create a Session
```python
from agents.memory_agent import MemoryAgent, SaveSessionInput
from agents.base_agent import AgentContext

agent = MemoryAgent()
input_data = SaveSessionInput(
    preferences={"default_color_scheme": "blue"}
)
context = AgentContext(session_id="new", workflow_id="create_session")
result = await agent.execute(input_data, context)
```

### Export Session
```python
from agents.memory_agent import ExportSessionInput

input_data = ExportSessionInput(
    session_id=session_id,
    include_sites=True,
    compress=True
)
result = await agent.execute(input_data, context)
exported_data = result.data["data"]
```

### Import Session
```python
from agents.memory_agent import ImportSessionInput

input_data = ImportSessionInput(
    data=exported_data,
    compressed=True
)
result = await agent.execute(input_data, context)
new_session_id = result.data["session_id"]
```

## Database Schema
The Memory Agent works with the following tables:
- `sessions` - User sessions
- `user_preferences` - User preferences (alternative to JSON in sessions)
- `sites` - Site records
- `site_versions` - Version history
- `audits` - Audit results
- `deployments` - Deployment records

## Configuration
Settings in `backend/utils/config.py`:
- `SESSION_TTL_HOURS`: Redis cache TTL (default: 24)
- `SESSION_CLEANUP_DAYS`: Retention period (default: 90)
- `DATABASE_POOL_SIZE`: Connection pool size (default: 20)
- `REDIS_MAX_CONNECTIONS`: Redis connection pool (default: 50)

## Testing
To test the Memory Agent:
```bash
# Run Celery worker
celery -A services.celery_app worker --loglevel=info

# Run Celery beat for scheduled tasks
celery -A services.celery_app beat --loglevel=info

# Test API endpoints
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"preferences": {"default_color_scheme": "blue"}}'
```

## Requirements Met
- ✅ 6.1: User preferences persistence
- ✅ 6.2: Site version storage and metadata
- ✅ 6.3: Session state retrieval
- ✅ 6.4: Audit history maintenance
- ✅ 6.5: 90-day data retention with automatic cleanup
