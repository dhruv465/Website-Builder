# Agent Orchestrator Implementation

## Overview

The Agent Orchestrator is the central coordination layer for the Smart Website Builder that manages agent execution, workflow state, error recovery, and observability.

## Components Implemented

### 1. Core Orchestrator (`orchestrator.py`)

**Key Features:**
- Agent registration and lifecycle management (REGISTERED → READY → EXECUTING → COMPLETED/FAILED)
- Workflow execution with state management (CREATE_SITE, UPDATE_SITE, AUDIT_ONLY, DEPLOY_ONLY)
- Context management for passing data between agents
- Redis integration for real-time state tracking
- Callback system for workflow events
- Comprehensive metrics collection

**Classes:**
- `WorkflowType`: Enum for workflow types
- `WorkflowStatus`: Enum for workflow execution status
- `AgentLifecycle`: Enum for agent lifecycle states
- `WorkflowMetrics`: Metrics tracking for workflows
- `WorkflowState`: State management for workflow execution
- `AgentOrchestrator`: Main orchestrator class

**Key Methods:**
- `register_agent()`: Register agents with the orchestrator
- `execute_workflow()`: Execute a complete workflow
- `execute_agent()`: Execute a single agent with retry logic
- `get_workflow_status()`: Get current workflow status
- `cancel_workflow()`: Cancel a running workflow
- `persist_workflow_logs()`: Save logs to database

### 2. Retry Handler (`retry_handler.py`)

**Key Features:**
- Exponential backoff retry logic
- Configurable retry parameters (max retries, delays, jitter)
- Automatic detection of retryable errors
- Retry callbacks for monitoring

**Classes:**
- `RetryConfig`: Configuration for retry behavior

**Functions:**
- `is_retryable_error()`: Determine if an error is retryable
- `retry_with_backoff()`: Execute function with retry logic
- `with_retry()`: Decorator for adding retry logic

### 3. WebSocket Manager (`websocket_manager.py`)

**Key Features:**
- Real-time workflow progress updates
- Log entry broadcasting
- Agent status notifications
- Workflow completion/error notifications
- Connection management per workflow

**Classes:**
- `WebSocketManager`: Manager for WebSocket connections

**Key Methods:**
- `connect()`: Connect client to workflow
- `disconnect()`: Disconnect client from workflow
- `broadcast()`: Broadcast message to all clients
- `send_progress_update()`: Send progress updates
- `send_log_entry()`: Send log entries
- `send_agent_status()`: Send agent status updates

### 4. Metrics Service (`metrics_service.py`)

**Key Features:**
- Database persistence for logs and metrics
- Metrics aggregation and analysis
- Trend analysis over time
- Prometheus format export
- Batch log saving

**Classes:**
- `MetricsService`: Service for managing metrics and logs

**Key Methods:**
- `save_workflow_log()`: Save single log entry
- `save_workflow_logs_batch()`: Save multiple logs
- `get_workflow_logs()`: Retrieve logs with filtering
- `update_agent_metrics()`: Update agent performance metrics
- `get_agent_metrics_summary()`: Get aggregated metrics
- `get_metrics_trends()`: Get trend data
- `export_metrics_prometheus()`: Export in Prometheus format
- `cleanup_old_logs()`: Remove old logs

### 5. Celery Tasks (`tasks.py`)

**New Tasks:**
- `persist_workflow_logs`: Persist workflow logs to database
- `cleanup_old_logs`: Daily cleanup of old logs (90 days)
- `cleanup_old_workflows`: Hourly cleanup of old workflow states (24 hours)

**Scheduled Tasks:**
- Old sessions cleanup: Daily at 2 AM UTC
- Old logs cleanup: Daily at 3 AM UTC
- Old workflows cleanup: Every hour

## Workflow Execution Flow

1. **Workflow Initialization**
   - Create workflow ID and state
   - Initialize metrics tracking
   - Save state to Redis
   - Create agent context

2. **Agent Execution**
   - Update agent lifecycle state
   - Send WebSocket status update
   - Execute agent with retry logic
   - Record execution metrics
   - Store output in context
   - Update workflow state

3. **Error Handling**
   - Detect retryable errors
   - Apply exponential backoff
   - Log retry attempts
   - Update error metrics
   - Trigger error callbacks

4. **Workflow Completion**
   - Update final status
   - Calculate total metrics
   - Save state to Redis
   - Trigger completion callbacks
   - Send WebSocket notification
   - Persist logs to database

## State Management

### In-Memory State
- Active workflow states
- Agent lifecycle states
- Real-time metrics

### Redis State
- Workflow state snapshots
- Session data
- Agent metrics cache

### Database State
- Workflow logs (persistent)
- Agent metrics (persistent)
- Historical data

## Metrics Tracked

### Workflow Metrics
- Total duration
- Agent execution times
- LLM API calls and token usage
- Error count
- Retry count

### Agent Metrics
- Execution count
- Success/error counts
- Average execution time
- Last execution time
- Success/error rates

### Log Metrics
- Total logs by level
- Logs per agent
- Error trends over time

## Error Recovery

### Retry Strategy
- Network errors: 3 retries with exponential backoff
- LLM errors: Configurable retries
- Validation errors: No retry (user intervention required)
- Timeout errors: 1 retry with increased timeout

### Backoff Configuration
- Initial delay: 1 second
- Maximum delay: 30 seconds
- Exponential base: 2.0
- Jitter: Enabled (0.5-1.5x multiplier)

## WebSocket Events

### Client → Server
- `workflow.start`: Start a workflow
- `workflow.cancel`: Cancel a workflow
- `ping`: Keep connection alive

### Server → Client
- `progress`: Workflow progress update
- `log`: New log entry
- `agent_status`: Agent status change
- `complete`: Workflow completed
- `error`: Workflow error

## Integration Points

### With Agents
- Agents register with orchestrator
- Orchestrator manages agent lifecycle
- Context passed between agents
- Metrics collected automatically

### With Redis
- Real-time state updates
- Session management
- Workflow state caching

### With Database
- Log persistence
- Metrics storage
- Historical analysis

### With WebSocket
- Real-time progress updates
- Live log streaming
- Agent status notifications

## Usage Example

```python
from services.orchestrator import orchestrator, WorkflowType
from agents.memory_agent import MemoryAgent

# Register agents
memory_agent = MemoryAgent()
orchestrator.register_agent(memory_agent)

# Execute workflow
result = await orchestrator.execute_workflow(
    workflow_type=WorkflowType.CREATE_SITE,
    input_data={"user_input": "Create a portfolio website"},
    session_id="session-123",
    user_preferences={"theme": "dark"}
)

# Get workflow status
status = orchestrator.get_workflow_status(result["workflow_id"])

# Get metrics
metrics = orchestrator.get_agent_metrics()
```

## Configuration

Key settings in `utils/config.py`:
- `MAX_RETRIES`: Maximum retry attempts (default: 3)
- `AGENT_TIMEOUT_SECONDS`: Agent execution timeout (default: 300)
- `SESSION_TTL_HOURS`: Session TTL in Redis (default: 24)
- `SESSION_CLEANUP_DAYS`: Days to keep sessions (default: 90)

## Future Enhancements

1. **Parallel Agent Execution**: Execute independent agents in parallel
2. **Circuit Breaker**: Stop calling failing services after threshold
3. **Rate Limiting**: Limit agent execution rate
4. **Workflow Templates**: Pre-defined workflow configurations
5. **Advanced Metrics**: More detailed performance analysis
6. **Distributed Tracing**: Full request tracing across services

## Testing

To test the orchestrator:

```python
# Unit tests
pytest backend/tests/test_orchestrator.py

# Integration tests
pytest backend/tests/test_workflow_integration.py
```

## Monitoring

### Prometheus Metrics
Access metrics at `/metrics` endpoint:
- `agent_execution_count`: Total executions per agent
- `agent_success_count`: Successful executions
- `agent_error_count`: Failed executions
- `agent_average_duration_seconds`: Average execution time

### Logs
Structured JSON logs with:
- Timestamp
- Level (info/warning/error)
- Agent name
- Workflow ID
- Message
- Metadata

## Dependencies

- FastAPI: Web framework
- Redis: State caching
- PostgreSQL: Persistent storage
- Celery: Background tasks
- SQLAlchemy: ORM
- Pydantic: Data validation
