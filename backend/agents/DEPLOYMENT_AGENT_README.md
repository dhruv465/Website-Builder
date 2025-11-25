# Deployment Agent Implementation

## Overview

The Deployment Agent is responsible for deploying websites to Vercel hosting platform. It validates HTML code, manages Vercel projects, deploys sites, verifies deployment health, and tracks deployment metrics.

## Components Implemented

### 1. Vercel API Client (`services/vercel_client.py`)

A comprehensive wrapper around the Vercel REST API providing:

**Features:**
- Project creation and management
- Deployment operations with file upload
- Deployment status polling with async/await
- Health verification of deployed sites
- Deployment history retrieval
- Authentication with API token from environment variables

**Key Methods:**
- `create_project()` - Create new Vercel project
- `get_project()` - Retrieve project by name or ID
- `update_project()` - Update project settings
- `create_deployment()` - Deploy HTML content
- `get_deployment()` - Get deployment status
- `wait_for_deployment()` - Poll until deployment completes
- `verify_deployment_health()` - Check if deployment is accessible
- `list_deployments()` - Get deployment history
- `delete_deployment()` - Remove a deployment

**Configuration:**
- Uses `VERCEL_API_TOKEN` from environment variables
- Base URL: `https://api.vercel.com`
- API Version: v13
- Default timeout: 60 seconds

### 2. Deployment Agent (`agents/deployment_agent.py`)

The main agent class that orchestrates the deployment process.

**Features:**
- HTML validation before deployment
- Unique site name generation
- Project creation or update handling
- Deployment with retry logic and exponential backoff
- Health verification
- Database record storage
- Deployment metrics tracking
- Manual deployment instructions as fallback

**Input Model:**
```python
class DeploymentInput:
    html_code: str              # HTML to deploy
    site_name: Optional[str]    # Desired site name
    site_id: Optional[str]      # Site ID for tracking
    project_id: Optional[str]   # Existing project ID for updates
    environment: str            # production or preview
```

**Output Model:**
```python
class DeploymentOutput:
    success: bool
    deployment_metadata: Optional[DeploymentMetadata]
    deployment_validation: Optional[DeploymentValidation]
    manual_instructions: Optional[str]
```

**Validation:**
- Checks for valid HTML structure
- Verifies presence of DOCTYPE, html, head, and body tags
- Validates minimum content requirements
- Calculates confidence score based on validation results

**Error Handling:**
- Retry logic with exponential backoff (3 retries max)
- Transient failure detection and retry
- Clear error messages for different failure types
- Manual deployment instructions as fallback
- Comprehensive logging of all attempts

**Metrics Tracking:**
- Build time measurement
- Success rate calculation
- Health check results
- Deployment environment tracking
- Update vs. new deployment tracking

### 3. API Endpoints (`api/deploy.py`)

RESTful API endpoints for deployment operations.

**Endpoints:**

#### POST `/api/deploy`
Deploy a site to Vercel.

**Request:**
```json
{
  "html_code": "<!DOCTYPE html>...",
  "site_name": "my-site",
  "site_id": "uuid",
  "session_id": "uuid",
  "workflow_id": "optional-uuid",
  "project_id": "optional-vercel-project-id",
  "environment": "production",
  "async_processing": false
}
```

**Response:**
```json
{
  "success": true,
  "url": "https://my-site.vercel.app",
  "deployment_id": "dpl_xxx",
  "project_id": "prj_xxx",
  "project_name": "my-site",
  "build_time": 5000,
  "is_update": false,
  "health_check_passed": true,
  "workflow_id": "uuid",
  "message": "Site deployed successfully"
}
```

#### GET `/api/deploy/status/{deployment_id}`
Get deployment status from Vercel.

**Response:**
```json
{
  "deployment_id": "dpl_xxx",
  "url": "https://my-site.vercel.app",
  "status": "ready",
  "build_time": 5000,
  "created_at": "2024-01-01T00:00:00"
}
```

#### GET `/api/deploy/history/{site_id}`
Get deployment history for a site.

**Query Parameters:**
- `limit` (optional): Maximum number of deployments to return (default: 20)

**Response:**
```json
{
  "site_id": "uuid",
  "deployments": [
    {
      "deployment_id": "dpl_xxx",
      "url": "https://my-site.vercel.app",
      "status": "success",
      "build_time": 5000,
      "created_at": "2024-01-01T00:00:00"
    }
  ],
  "total": 1
}
```

#### GET `/api/deploy/task/{task_id}`
Get status of async deployment task.

**Response:**
```json
{
  "task_id": "task-uuid",
  "status": "success",
  "result": {
    "success": true,
    "url": "https://my-site.vercel.app",
    ...
  }
}
```

#### POST `/api/deploy/rollback/{site_id}`
Rollback to a previous deployment.

**Query Parameters:**
- `deployment_id`: Deployment ID to rollback to

**Response:**
Same as POST `/api/deploy`

### 4. Database Integration

**Deployment Model:**
- Stores deployment records in PostgreSQL
- Links deployments to sites
- Tracks deployment metadata (URL, ID, build time, status)
- Maintains deployment history

**Repository Methods:**
- `save_deployment()` - Store deployment record
- `get_deployments_by_site()` - Retrieve deployment history

## Configuration

### Environment Variables

```bash
# Vercel API Token (required for automated deployment)
VERCEL_API_TOKEN=your_vercel_token_here

# Get token from: https://vercel.com/account/tokens
```

### Settings

From `utils/config.py`:
```python
VERCEL_API_TOKEN: str = ""  # Optional, enables automated deployment
```

## Usage Examples

### Basic Deployment

```python
from agents.deployment_agent import deployment_agent, DeploymentInput
from agents.base_agent import AgentContext

# Create input
input_data = DeploymentInput(
    html_code="<!DOCTYPE html><html>...</html>",
    site_name="my-awesome-site",
    site_id="site-uuid",
    environment="production"
)

# Create context
context = AgentContext(
    session_id="session-uuid",
    workflow_id="workflow-uuid"
)

# Execute deployment
result = await deployment_agent.execute_with_metrics(input_data, context)

if result.success:
    print(f"Deployed to: {result.deployment_metadata.url}")
```

### Update Existing Deployment

```python
input_data = DeploymentInput(
    html_code="<!DOCTYPE html><html>...</html>",
    site_name="my-awesome-site",
    site_id="site-uuid",
    project_id="prj_existing_project_id",  # Existing project
    environment="production"
)

result = await deployment_agent.execute_with_metrics(input_data, context)
```

### API Usage

```bash
# Deploy a site
curl -X POST http://localhost:8000/api/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "html_code": "<!DOCTYPE html><html>...</html>",
    "site_name": "my-site",
    "session_id": "uuid",
    "environment": "production"
  }'

# Get deployment status
curl http://localhost:8000/api/deploy/status/dpl_xxx

# Get deployment history
curl http://localhost:8000/api/deploy/history/site-uuid?limit=10
```

## Error Handling

### Retry Logic

The deployment agent implements exponential backoff retry logic:

- **Max Retries:** 3
- **Initial Delay:** 2 seconds
- **Max Delay:** 30 seconds
- **Exponential Base:** 2.0
- **Jitter:** Enabled (adds randomness to prevent thundering herd)

### Error Types

1. **Validation Errors** (Not retryable)
   - Invalid HTML structure
   - Missing required tags
   - Empty content

2. **Network Errors** (Retryable)
   - Connection failures
   - Timeout errors
   - Transient API failures

3. **Deployment Errors** (Retryable)
   - Vercel build failures
   - Deployment state errors
   - Health check failures

4. **Timeout Errors** (Retryable)
   - Deployment taking too long
   - Health check timeout

### Fallback Strategy

If automated deployment fails after all retries:
1. Agent provides manual deployment instructions
2. Instructions include multiple hosting options (Vercel, Netlify, GitHub Pages, etc.)
3. User can deploy manually using the generated HTML
4. Response includes `manual_instructions` field

## Metrics and Monitoring

### Tracked Metrics

- **Build Time:** Time taken to build and deploy (milliseconds)
- **Success Rate:** Percentage of successful deployments
- **Health Check Status:** Whether deployed site is accessible
- **Retry Count:** Number of retry attempts
- **Deployment Type:** New deployment vs. update
- **Environment:** Production vs. preview

### Logging

All deployment operations are logged with structured metadata:

```python
logger.info(
    "Deployment metrics",
    extra={
        "deployment_id": "dpl_xxx",
        "project_id": "prj_xxx",
        "build_time_ms": 5000,
        "environment": "production",
        "is_update": False,
        "health_check_passed": True,
        "timestamp": "2024-01-01T00:00:00"
    }
)
```

## WebSocket Integration

The deployment agent sends real-time updates via WebSocket:

```javascript
// Agent status updates
{
  "type": "agent_status",
  "agent": "DeploymentAgent",
  "status": "working",  // or "done", "error"
  "message": "Deploying site..."
}
```

## Testing

### Unit Tests

Test the deployment agent in isolation:

```python
# Mock Vercel API responses
# Test HTML validation
# Test site name sanitization
# Test error handling
# Test retry logic
```

### Integration Tests

Test the complete deployment workflow:

```python
# Test end-to-end deployment
# Test deployment updates
# Test rollback functionality
# Test health verification
```

## Requirements Satisfied

This implementation satisfies the following requirements from the design document:

- **Requirement 4.1:** Deploy sites to Vercel hosting platform
- **Requirement 4.2:** Provide live URL within 5 minutes
- **Requirement 4.3:** Clear error messages and retry options
- **Requirement 4.4:** Support deployment to Vercel as primary platform
- **Requirement 4.5:** Store deployment metadata
- **Requirement 8.3:** Error handling and retry logic
- **Requirement 10.1:** Real-time status updates

## Future Enhancements

1. **Custom Domains:** Support for custom domain configuration
2. **Environment Variables:** Support for environment variable injection
3. **Build Configuration:** Custom build settings and framework detection
4. **Preview Deployments:** Automatic preview deployments for testing
5. **Deployment Aliases:** Support for deployment aliases and URLs
6. **Multi-file Deployments:** Support for deploying multiple files
7. **Asset Optimization:** Automatic image and asset optimization
8. **CDN Configuration:** Custom CDN settings
9. **Analytics Integration:** Deployment analytics and monitoring
10. **Cost Tracking:** Track deployment costs and usage

## Troubleshooting

### Common Issues

**Issue:** "Vercel API token not configured"
- **Solution:** Set `VERCEL_API_TOKEN` environment variable
- **Fallback:** Use manual deployment instructions

**Issue:** "Deployment timeout"
- **Solution:** Increase timeout in settings or retry
- **Check:** Vercel service status

**Issue:** "Health check failed"
- **Solution:** Verify HTML is valid and renders correctly
- **Check:** Deployment URL manually in browser

**Issue:** "Project name already exists"
- **Solution:** Use a different site name or provide existing project_id
- **Auto-handled:** Agent will fetch existing project

## Dependencies

- `httpx` - Async HTTP client for Vercel API
- `beautifulsoup4` - HTML parsing and validation
- `pydantic` - Data validation and serialization
- `sqlalchemy` - Database ORM
- `celery` - Async task processing

## API Documentation

Full API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
