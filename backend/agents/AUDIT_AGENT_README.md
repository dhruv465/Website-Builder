# Audit Agent Implementation

## Overview

The Audit Agent evaluates generated websites against SEO, accessibility, and performance criteria. It provides detailed issue reports with fix suggestions and calculates confidence scores for each category.

## Components Implemented

### 1. Audit Agent (`backend/agents/audit_agent.py`)

**Key Features:**
- Evaluates HTML code for SEO compliance
- Checks accessibility using WCAG guidelines
- Analyzes performance metrics
- Uses Gemini AI for semantic quality analysis
- Generates detailed issue reports with severity levels
- Calculates confidence scores for each category
- Supports audit comparison with previous audits

**Audit Categories:**

#### SEO Checks
- Meta tags (title, description, keywords)
- Heading hierarchy (H1, H2, etc.)
- Image alt attributes
- Semantic HTML usage
- Open Graph tags
- Structured data markup

#### Accessibility Checks
- ARIA labels and roles
- Color contrast (basic check)
- Keyboard navigation support
- Form label associations
- Alt text for images
- Semantic landmarks
- Language attribute
- Skip navigation links

#### Performance Checks
- Resource count and size estimation
- Image optimization (format, lazy loading)
- CSS/JS minification potential
- Render-blocking resources
- Font loading strategy
- DOM size analysis
- Viewport meta tag

**Scoring System:**
- Each category scored 0-100
- Overall score is weighted average:
  - SEO: 30%
  - Accessibility: 40% (most important)
  - Performance: 30%

**Issue Severity Levels:**
- CRITICAL: Major issues that must be fixed
- WARNING: Important issues that should be addressed
- INFO: Minor improvements or suggestions

### 2. Audit Repository (`backend/repositories/audit_repository.py`)

**Key Features:**
- Create and store audit results in database
- Create and store audit issues with details
- Retrieve audit history for a site
- Get latest audit for comparison
- Calculate audit trends over time
- Filter issues by severity
- Transaction management with context managers

**Key Methods:**
- `create_audit()`: Store audit results
- `create_audit_issue()`: Store individual issues
- `get_audit_by_id()`: Retrieve audit with issues
- `get_audits_by_site()`: Get audit history
- `get_latest_audit()`: Get most recent audit
- `get_audit_trends()`: Calculate trends and improvements
- `get_issues_by_severity()`: Filter issues

### 3. Audit API Endpoints (`backend/api/audit.py`)

**Endpoints:**

#### POST `/api/audit/run`
Run audit on HTML code.

**Request:**
```json
{
  "html_code": "<html>...</html>",
  "site_id": "uuid",
  "site_version_id": "uuid",
  "session_id": "uuid",
  "workflow_id": "optional-workflow-id",
  "async_processing": false
}
```

**Response:**
```json
{
  "success": true,
  "audit_result": {
    "seo": {
      "score": 85,
      "summary": "Good SEO practices...",
      "suggestions": [...],
      "issues": [...],
      "confidence": 0.9
    },
    "accessibility": {...},
    "performance": {...},
    "overall_score": 82,
    "improvement_from_previous": 5
  },
  "audit_id": "uuid",
  "confidence": 0.85,
  "workflow_id": "workflow-id",
  "message": "Audit completed successfully"
}
```

#### GET `/api/audit/history/{site_id}`
Get audit history for a site.

**Query Parameters:**
- `limit`: Maximum number of audits to return (default: 10)

**Response:**
```json
{
  "site_id": "uuid",
  "audits": [
    {
      "id": "uuid",
      "overall_score": 82,
      "seo_score": 85,
      "accessibility_score": 80,
      "performance_score": 81,
      "created_at": "2024-11-16T12:00:00Z",
      "issue_count": 5
    }
  ],
  "count": 10
}
```

#### GET `/api/audit/trends/{site_id}`
Get audit trends over time.

**Query Parameters:**
- `days`: Number of days to look back (default: 30, max: 365)

**Response:**
```json
{
  "site_id": "uuid",
  "period_days": 30,
  "audit_count": 5,
  "trends": [
    {
      "timestamp": "2024-11-16T12:00:00Z",
      "overall_score": 82,
      "seo_score": 85,
      "accessibility_score": 80,
      "performance_score": 81
    }
  ],
  "average_scores": {
    "overall": 80.5,
    "seo": 83.2,
    "accessibility": 78.5,
    "performance": 79.8
  },
  "improvement": {
    "overall": 10,
    "seo": 5,
    "accessibility": 15,
    "performance": 8
  },
  "latest_audit": {
    "id": "uuid",
    "timestamp": "2024-11-16T12:00:00Z",
    "overall_score": 82
  }
}
```

## Database Schema

The audit data is stored in two tables:

### `audits` Table
- `id`: UUID primary key
- `site_id`: UUID foreign key to sites
- `site_version_id`: UUID foreign key to site_versions (optional)
- `seo_score`: Integer (0-100)
- `accessibility_score`: Integer (0-100)
- `performance_score`: Integer (0-100)
- `overall_score`: Integer (0-100)
- `details`: JSON with full audit results
- `created_at`: Timestamp

### `audit_issues` Table
- `id`: UUID primary key
- `audit_id`: UUID foreign key to audits
- `category`: String (seo, accessibility, performance)
- `severity`: Enum (critical, warning, info)
- `description`: Text
- `location`: String (line number or CSS selector)
- `fix_suggestion`: Text
- `created_at`: Timestamp

## Usage Example

```python
from agents.audit_agent import AuditAgent, AuditInput
from agents.base_agent import AgentContext

# Initialize agent
agent = AuditAgent()

# Create input
input_data = AuditInput(
    html_code="<html>...</html>",
    site_id="site-uuid"
)

# Create context
context = AgentContext(
    session_id="session-uuid",
    workflow_id="workflow-uuid"
)

# Execute audit
result = await agent.execute_with_metrics(input_data, context)

# Access results
if result.success:
    audit = result.audit_result
    print(f"Overall Score: {audit.overall_score}")
    print(f"SEO Score: {audit.seo.score}")
    print(f"Issues: {len(audit.seo.issues)}")
```

## Integration with Workflow

The Audit Agent integrates into the workflow as follows:

1. **CREATE_SITE Workflow**: Input → Code → **Audit** → Deploy
2. **UPDATE_SITE Workflow**: Memory → Code → **Audit** → Deploy
3. **AUDIT_ONLY Workflow**: Memory → **Audit**

The agent automatically:
- Compares with previous audits
- Stores results in database
- Sends WebSocket updates for real-time progress
- Supports async processing via Celery

## Quality Thresholds

The system defines minimum quality thresholds:
- SEO: 70
- Accessibility: 80
- Performance: 75
- Overall: 75

When scores fall below these thresholds, the automatic improvement workflow is triggered.

## Confidence Scoring

Each category has a confidence score (0.0-1.0):
- SEO: 0.9 (high confidence for automated checks)
- Accessibility: 0.85 (slightly lower due to heuristic checks)
- Performance: 0.8 (lower as we can't measure actual load times)

Overall confidence is the average of category confidences.

## Future Enhancements

- Color contrast ratio calculation
- Lighthouse integration for real performance metrics
- Custom audit rules configuration
- Automated fix application
- A/B testing support
- Competitive analysis
