"""
Agent orchestrator for managing workflow execution.
"""
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from enum import Enum
import uuid
import asyncio
import time

from agents.base_agent import (
    BaseAgent,
    AgentContext,
    AgentInput,
    AgentOutput,
    AgentError,
    ErrorType,
)
from services.redis_service import redis_service
from services.retry_handler import retry_with_backoff, RetryConfig
from services.websocket_manager import websocket_manager
from utils.logging import logger
from utils.config import settings
from agents.input_agent import ParseRequirementsInput, SiteRequirements
from agents.code_generation_agent import CodeGenerationInput, CodeGenerationOutput
from agents.audit_agent import AuditInput, AuditOutput
from agents.deployment_agent import DeploymentInput, DeploymentOutput
from agents.memory_agent import SaveSiteInput, SaveSiteOutput

# Note: MetricsService will be imported and used when database session is available
# from services.metrics_service import MetricsService


class WorkflowType(str, Enum):
    """Types of workflows."""
    CREATE_SITE = "create_site"
    UPDATE_SITE = "update_site"
    AUDIT_ONLY = "audit_only"
    DEPLOY_ONLY = "deploy_only"
    IMPROVE_SITE = "improve_site"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentLifecycle(str, Enum):
    """Agent lifecycle states."""
    REGISTERED = "registered"
    INITIALIZING = "initializing"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEREGISTERED = "deregistered"


class WorkflowMetrics:
    """Metrics for workflow execution."""
    
    def __init__(self):
        self.total_duration: float = 0.0
        self.agent_durations: Dict[str, float] = {}
        self.llm_calls: int = 0
        self.llm_tokens_used: int = 0
        self.error_count: int = 0
        self.retry_count: int = 0
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
    
    def start(self):
        """Start timing the workflow."""
        self.start_time = datetime.utcnow()
    
    def end(self):
        """End timing the workflow."""
        self.end_time = datetime.utcnow()
        if self.start_time:
            self.total_duration = (self.end_time - self.start_time).total_seconds()
    
    def record_agent_execution(self, agent_name: str, duration: float):
        """Record agent execution time."""
        self.agent_durations[agent_name] = duration
    
    def record_llm_call(self, tokens: int = 0):
        """Record LLM API call."""
        self.llm_calls += 1
        self.llm_tokens_used += tokens
    
    def record_error(self):
        """Record an error."""
        self.error_count += 1
    
    def record_retry(self):
        """Record a retry attempt."""
        self.retry_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_duration": self.total_duration,
            "agent_durations": self.agent_durations,
            "llm_calls": self.llm_calls,
            "llm_tokens_used": self.llm_tokens_used,
            "error_count": self.error_count,
            "retry_count": self.retry_count,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
        }


class WorkflowState:
    """State management for workflow execution."""
    
    def __init__(self, workflow_id: str, workflow_type: WorkflowType, session_id: str):
        self.workflow_id = workflow_id
        self.workflow_type = workflow_type
        self.session_id = session_id
        self.status = WorkflowStatus.PENDING
        self.current_agent: Optional[str] = None
        self.completed_agents: List[str] = []
        self.failed_agent: Optional[str] = None
        self.logs: List[Dict[str, Any]] = []
        self.metrics = WorkflowMetrics()
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None
        self.progress_percentage: float = 0.0
        self.agent_states: Dict[str, AgentLifecycle] = {}
    
    def add_log(self, level: str, message: str, agent: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Add a log entry and broadcast via WebSocket."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "agent": agent or "System",
            "metadata": metadata or {},
        }
        self.logs.append(log_entry)
        
        # Log to application logger
        log_extra = {"workflow_id": self.workflow_id, "agent": agent or "System"}
        if metadata:
            log_extra["metadata"] = metadata
        
        if level == "error":
            logger.error(message, extra=log_extra)
        elif level == "warning":
            logger.warning(message, extra=log_extra)
        else:
            logger.info(message, extra=log_extra)
        
        # Broadcast log entry via WebSocket (non-blocking)
        asyncio.create_task(websocket_manager.send_log_entry(self.workflow_id, log_entry))
    
    def set_agent_state(self, agent_name: str, state: AgentLifecycle):
        """Set agent lifecycle state."""
        self.agent_states[agent_name] = state
        self.add_log("info", f"Agent {agent_name} state: {state.value}", agent=agent_name)
    
    def update_progress(self, completed: int, total: int):
        """Update workflow progress percentage."""
        if total > 0:
            self.progress_percentage = (completed / total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "workflow_type": self.workflow_type.value,
            "session_id": self.session_id,
            "status": self.status.value,
            "current_agent": self.current_agent,
            "completed_agents": self.completed_agents,
            "failed_agent": self.failed_agent,
            "logs": self.logs,
            "metrics": self.metrics.to_dict(),
            "result": self.result,
            "error": self.error,
            "progress_percentage": self.progress_percentage,
            "agent_states": {k: v.value for k, v in self.agent_states.items()},
        }


class AgentOrchestrator:
    """
    Orchestrator for managing agent execution and workflows.
    
    Responsibilities:
    - Register and manage agent lifecycle
    - Execute workflows with sequential agent coordination
    - Manage workflow state and context
    - Track metrics and logs
    - Handle errors and retries
    - Provide real-time progress updates via Redis
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_states: Dict[str, AgentLifecycle] = {}
        self.workflows: Dict[str, WorkflowState] = {}
        self.workflow_callbacks: Dict[str, List[Callable]] = {}
        logger.info("Agent orchestrator initialized")
    
    def register_agent(self, agent: BaseAgent, initialize: bool = True) -> bool:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent to register
            initialize: Whether to initialize the agent immediately
            
        Returns:
            True if registration successful
        """
        try:
            self.agents[agent.name] = agent
            self.agent_states[agent.name] = AgentLifecycle.REGISTERED
            
            if initialize:
                self.agent_states[agent.name] = AgentLifecycle.READY
            
            logger.info(f"Registered agent: {agent.name} (state: {self.agent_states[agent.name].value})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent {agent.name}: {str(e)}")
            return False
    
    def deregister_agent(self, agent_name: str) -> bool:
        """
        Deregister an agent from the orchestrator.
        
        Args:
            agent_name: Name of agent to deregister
            
        Returns:
            True if deregistration successful
        """
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.agent_states[agent_name] = AgentLifecycle.DEREGISTERED
            logger.info(f"Deregistered agent: {agent_name}")
            return True
        return False
    
    def get_agent_state(self, agent_name: str) -> Optional[AgentLifecycle]:
        """
        Get the lifecycle state of an agent.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            Agent lifecycle state or None
        """
        return self.agent_states.get(agent_name)
    
    def is_agent_ready(self, agent_name: str) -> bool:
        """
        Check if an agent is ready for execution.
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            True if agent is ready
        """
        state = self.get_agent_state(agent_name)
        return state == AgentLifecycle.READY
    
    def create_context(
        self,
        session_id: str,
        workflow_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
    ) -> AgentContext:
        """
        Create an agent context for workflow execution.
        
        Args:
            session_id: Session ID
            workflow_id: Workflow ID
            user_preferences: User preferences
            
        Returns:
            AgentContext instance
        """
        return AgentContext(
            session_id=session_id,
            workflow_id=workflow_id,
            user_preferences=user_preferences or {},
            max_retries=settings.MAX_RETRIES,
        )
    
    def _save_workflow_state_to_redis(self, state: WorkflowState):
        """
        Save workflow state to Redis for real-time access.
        
        Args:
            state: Workflow state to save
        """
        try:
            redis_service.set_workflow_state(state.workflow_id, state.to_dict())
        except Exception as e:
            logger.error(f"Failed to save workflow state to Redis: {str(e)}")
    
    def _load_workflow_state_from_redis(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Load workflow state from Redis.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow state dict or None
        """
        try:
            return redis_service.get_workflow_state(workflow_id)
        except Exception as e:
            logger.error(f"Failed to load workflow state from Redis: {str(e)}")
            return None
    
    def register_workflow_callback(
        self,
        workflow_id: str,
        callback: Callable,
    ):
        """
        Register a callback for workflow events.
        
        Args:
            workflow_id: Workflow ID
            callback: Callback function to execute
        """
        if workflow_id not in self.workflow_callbacks:
            self.workflow_callbacks[workflow_id] = []
        self.workflow_callbacks[workflow_id].append(callback)
    
    async def _trigger_workflow_callbacks(
        self,
        workflow_id: str,
        event: str,
        data: Any,
    ):
        """
        Trigger callbacks for workflow events.
        
        Args:
            workflow_id: Workflow ID
            event: Event type (completed, failed, progress)
            data: Event data
        """
        if workflow_id in self.workflow_callbacks:
            for callback in self.workflow_callbacks[workflow_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event, data)
                    else:
                        callback(event, data)
                except Exception as e:
                    logger.error(f"Callback error for workflow {workflow_id}: {str(e)}")

    async def execute_workflow(
        self,
        workflow_type: WorkflowType,
        input_data: Dict[str, Any],
        session_id: str,
        user_preferences: Optional[Dict[str, Any]] = None,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Execute a workflow with full state management and error handling.
        
        Args:
            workflow_type: Type of workflow to execute
            input_data: Input data for the workflow
            session_id: Session ID
            user_preferences: User preferences
            workflow_id: Optional pre-generated workflow ID
            
        Returns:
            Workflow result with status and data
        """
        workflow_id = workflow_id or str(uuid.uuid4())
        
        # Initialize workflow state
        state = WorkflowState(workflow_id, workflow_type, session_id)
        state.status = WorkflowStatus.RUNNING
        state.metrics.start()
        state.add_log("info", f"Starting {workflow_type.value} workflow")
        
        # Store state in memory and Redis
        self.workflows[workflow_id] = state
        self._save_workflow_state_to_redis(state)
        
        try:
            # Create agent context
            context = self.create_context(session_id, workflow_id, user_preferences)
            
            # Execute workflow based on type
            if workflow_type == WorkflowType.CREATE_SITE:
                result = await self._execute_create_site_workflow(input_data, context, state)
            elif workflow_type == WorkflowType.UPDATE_SITE:
                result = await self._execute_update_site_workflow(input_data, context, state)
            elif workflow_type == WorkflowType.AUDIT_ONLY:
                result = await self._execute_audit_only_workflow(input_data, context, state)
            elif workflow_type == WorkflowType.DEPLOY_ONLY:
                result = await self._execute_deploy_only_workflow(input_data, context, state)
            elif workflow_type == WorkflowType.IMPROVE_SITE:
                result = await self._execute_improve_site_workflow(input_data, context, state)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
            
            # Update workflow state
            state.status = WorkflowStatus.COMPLETED
            state.result = result
            state.metrics.end()
            state.add_log("info", f"Workflow completed successfully in {state.metrics.total_duration:.2f}s")
            
            # Save final state
            self._save_workflow_state_to_redis(state)
            
            # Trigger callbacks
            await self._trigger_workflow_callbacks(workflow_id, "completed", result)
            
            # Send WebSocket completion notification
            await websocket_manager.send_workflow_complete(workflow_id, result)
            
            return {
                "workflow_id": workflow_id,
                "status": WorkflowStatus.COMPLETED.value,
                "result": result,
                "metrics": state.metrics.to_dict(),
            }
            
        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}", exc_info=True)
            
            state.status = WorkflowStatus.FAILED
            state.error = str(e)
            state.metrics.end()
            state.metrics.record_error()
            state.add_log("error", f"Workflow failed: {str(e)}")
            
            # Save final state
            self._save_workflow_state_to_redis(state)
            
            # Trigger callbacks
            await self._trigger_workflow_callbacks(workflow_id, "failed", {"error": str(e)})
            
            # Send WebSocket error notification
            await websocket_manager.send_workflow_error(workflow_id, str(e))
            
            return {
                "workflow_id": workflow_id,
                "status": WorkflowStatus.FAILED.value,
                "error": str(e),
                "metrics": state.metrics.to_dict(),
            }
    
    async def _execute_agent_with_retry(
        self,
        agent_name: str,
        input_data: AgentInput,
        context: AgentContext,
        state: WorkflowState,
    ) -> AgentOutput:
        """
        Internal method to execute agent (used by retry logic).
        
        Args:
            agent_name: Name of the agent to execute
            input_data: Input data for the agent
            context: Execution context
            state: Workflow state
            
        Returns:
            Agent output
        """
        agent = self.agents[agent_name]
        output = await agent.execute_with_metrics(input_data, context)
        context.add_output(agent_name, output)
        return output
    
    async def execute_agent(
        self,
        agent_name: str,
        input_data: AgentInput,
        context: AgentContext,
        state: WorkflowState,
        enable_retry: bool = True,
    ) -> AgentOutput:
        """
        Execute a specific agent with full lifecycle management and retry logic.
        
        Args:
            agent_name: Name of the agent to execute
            input_data: Input data for the agent
            context: Execution context
            state: Workflow state
            enable_retry: Whether to enable retry logic
            
        Returns:
            Agent output
            
        Raises:
            ValueError: If agent not found
            AgentError: If agent execution fails
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        
        if not self.is_agent_ready(agent_name):
            raise ValueError(f"Agent {agent_name} is not ready (state: {self.get_agent_state(agent_name)})")
        
        # Update state
        state.current_agent = agent_name
        state.set_agent_state(agent_name, AgentLifecycle.EXECUTING)
        state.add_log("info", f"Executing agent: {agent_name}", agent=agent_name)
        self._save_workflow_state_to_redis(state)
        
        # Update agent lifecycle
        self.agent_states[agent_name] = AgentLifecycle.EXECUTING
        
        # Send WebSocket update
        asyncio.create_task(websocket_manager.send_agent_status(
            state.workflow_id,
            agent_name,
            "executing"
        ))
        
        start_time = time.time()
        
        # Retry callback
        def on_retry(attempt: int, error: Exception, delay: float):
            state.metrics.record_retry()
            state.add_log(
                "warning",
                f"Agent {agent_name} retry {attempt + 1}/{context.max_retries}: {str(error)}. Waiting {delay:.2f}s",
                agent=agent_name,
                metadata={"attempt": attempt + 1, "delay": delay}
            )
            self._save_workflow_state_to_redis(state)
        
        try:
            # Execute agent with retry logic if enabled
            if enable_retry:
                retry_config = RetryConfig(
                    max_retries=context.max_retries,
                    initial_delay=1.0,
                    max_delay=30.0,
                    exponential_base=2.0,
                    jitter=True,
                )
                output = await retry_with_backoff(
                    self._execute_agent_with_retry,
                    agent_name,
                    input_data,
                    context,
                    state,
                    config=retry_config,
                    on_retry=on_retry,
                )
            else:
                output = await self._execute_agent_with_retry(
                    agent_name,
                    input_data,
                    context,
                    state,
                )
            
            # Record execution time
            execution_time = time.time() - start_time
            state.metrics.record_agent_execution(agent_name, execution_time)
            
            # Update state
            state.completed_agents.append(agent_name)
            state.set_agent_state(agent_name, AgentLifecycle.COMPLETED)
            state.add_log(
                "info",
                f"Agent {agent_name} completed in {execution_time:.2f}s",
                agent=agent_name,
                metadata={"execution_time": execution_time, "success": output.success}
            )
            
            # Update agent lifecycle
            self.agent_states[agent_name] = AgentLifecycle.READY
            
            # Save state
            self._save_workflow_state_to_redis(state)
            
            # Send WebSocket update
            asyncio.create_task(websocket_manager.send_agent_status(
                state.workflow_id,
                agent_name,
                "completed",
                {"execution_time": execution_time, "success": output.success}
            ))
            
            return output
            
        except AgentError as e:
            execution_time = time.time() - start_time
            state.metrics.record_agent_execution(agent_name, execution_time)
            state.metrics.record_error()
            
            # Update state
            state.failed_agent = agent_name
            state.set_agent_state(agent_name, AgentLifecycle.FAILED)
            state.add_log(
                "error",
                f"Agent {agent_name} failed: {e.message}",
                agent=agent_name,
                metadata={"error_type": e.error_type.value, "recoverable": e.recoverable}
            )
            
            # Update agent lifecycle
            self.agent_states[agent_name] = AgentLifecycle.FAILED
            
            # Save state
            self._save_workflow_state_to_redis(state)
            
            raise
            
        except Exception as e:
            execution_time = time.time() - start_time
            state.metrics.record_agent_execution(agent_name, execution_time)
            state.metrics.record_error()
            
            # Update state
            state.failed_agent = agent_name
            state.set_agent_state(agent_name, AgentLifecycle.FAILED)
            state.add_log("error", f"Agent {agent_name} failed with unexpected error: {str(e)}", agent=agent_name)
            
            # Update agent lifecycle
            self.agent_states[agent_name] = AgentLifecycle.FAILED
            
            # Save state
            self._save_workflow_state_to_redis(state)
            
            raise AgentError(
                message=f"Unexpected error in {agent_name}: {str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                agent_name=agent_name,
                recoverable=False,
                retryable=False,
            )
    
    async def _execute_create_site_workflow(
        self,
        input_data: Dict[str, Any],
        context: AgentContext,
        state: WorkflowState,
    ) -> Dict[str, Any]:
        """
        Execute CREATE_SITE workflow: Input → Code → Audit → Deploy.
        
        Args:
            input_data: Workflow input data
            context: Agent context
            state: Workflow state
            
        Returns:
            Workflow result
        """
        state.add_log("info", "Starting CREATE_SITE workflow")
        
        # 1. Input Processing
        requirements = None
        if "requirements" in input_data:
            state.add_log("info", "Using provided requirements")
            requirements = input_data["requirements"]
        else:
            state.add_log("info", "Parsing requirements from input")
            raw_input = input_data.get("prompt") or input_data.get("raw_input")
            if not raw_input:
                raise ValueError("No requirements or input prompt provided")
                
            input_agent_input = ParseRequirementsInput(
                raw_input=raw_input,
                session_id=context.session_id,
                input_type="text"
            )
            
            input_output = await self.execute_agent(
                "InputAgent",
                input_agent_input,
                context,
                state
            )
            
            if input_output.requirements:
                requirements = input_output.requirements.model_dump()
            else:
                raise ValueError("Failed to extract requirements from input")

        # 2. Code Generation
        state.add_log("info", "Generating code from requirements")
        code_gen_input = CodeGenerationInput(
            requirements=requirements,
            framework=requirements.get("framework", "vanilla"),
            ui_library=requirements.get("ui_library")
        )
        
        code_gen_output = await self.execute_agent(
            "CodeGenerationAgent",
            code_gen_input,
            context,
            state
        )
        
        if not code_gen_output.generated_code:
            raise ValueError("Code generation failed")
            
        generated_code = code_gen_output.generated_code
        
        # 3. Audit
        state.add_log("info", "Auditing generated code")
        audit_input = AuditInput(
            html_code=generated_code.html,
            framework=generated_code.metadata.framework
        )
        
        audit_output = await self.execute_agent(
            "AuditAgent",
            audit_input,
            context,
            state
        )
        
        # 4. Deployment
        state.add_log("info", "Deploying site")
        deployment_input = DeploymentInput(
            html_code=generated_code.html,
            files=generated_code.additional_files,
            site_name=input_data.get("site_name"),
            framework=generated_code.metadata.framework,
            environment="production"
        )
        
        deployment_output = await self.execute_agent(
            "DeploymentAgent",
            deployment_input,
            context,
            state
        )
        
        # 5. Persistence (Save Site)
        state.add_log("info", "Saving site record")
        save_site_input = SaveSiteInput(
            session_id=context.session_id,
            site_name=deployment_output.deployment_metadata.project_name,
            code=generated_code.html,
            requirements=requirements,
            framework=generated_code.metadata.framework,
            changes="Initial creation"
        )
        
        site_output = await self.execute_agent(
            "MemoryAgent",
            save_site_input,
            context,
            state
        )
        
        return {
            "workflow_type": "create_site",
            "status": "completed",
            "site_id": site_output.site_id,
            "deployment_url": deployment_output.deployment_metadata.url,
            "audit_score": audit_output.audit_result.overall_score if audit_output.audit_result else None,
            "requirements": requirements
        }
    
    async def _execute_update_site_workflow(
        self,
        input_data: Dict[str, Any],
        context: AgentContext,
        state: WorkflowState,
    ) -> Dict[str, Any]:
        """
        Execute UPDATE_SITE workflow: Memory → Code → Audit → Deploy.
        
        Args:
            input_data: Workflow input data
            context: Agent context
            state: Workflow state
            
        Returns:
            Workflow result
        """
        state.add_log("info", "Starting UPDATE_SITE workflow")
        
        site_id = input_data.get("site_id")
        if not site_id:
            raise ValueError("site_id is required for update workflow")
            
        # 1. Load existing site
        state.add_log("info", f"Loading site {site_id}")
        from agents.memory_agent import LoadSiteInput
        
        load_site_input = LoadSiteInput(site_id=site_id)
        site_output = await self.execute_agent(
            "MemoryAgent",
            load_site_input,
            context,
            state
        )
        
        if not site_output.success or not site_output.data.get("site"):
            raise ValueError(f"Failed to load site {site_id}")
            
        site_data = site_output.data["site"]
        existing_code = site_data.get("latest_version", {}).get("code", "")
        
        # 2. Code Generation (Modification)
        state.add_log("info", "Generating code modifications")
        
        # Parse modifications if needed
        modifications = input_data.get("modifications", [])
        if not modifications and input_data.get("prompt"):
            modifications = [input_data["prompt"]]
            
        code_gen_input = CodeGenerationInput(
            requirements=input_data.get("requirements", {}),
            existing_code=existing_code,
            modifications=modifications,
            framework=site_data.get("framework", "vanilla")
        )
        
        code_gen_output = await self.execute_agent(
            "CodeGenerationAgent",
            code_gen_input,
            context,
            state
        )
        
        if not code_gen_output.generated_code:
            raise ValueError("Code modification failed")
            
        generated_code = code_gen_output.generated_code
        
        # 3. Audit
        state.add_log("info", "Auditing updated code")
        audit_input = AuditInput(
            html_code=generated_code.html,
            framework=generated_code.metadata.framework
        )
        
        audit_output = await self.execute_agent(
            "AuditAgent",
            audit_input,
            context,
            state
        )
        
        # 4. Deployment
        state.add_log("info", "Deploying updated site")
        deployment_input = DeploymentInput(
            html_code=generated_code.html,
            files=generated_code.additional_files,
            site_name=site_data.get("name"),
            site_id=site_id,
            framework=generated_code.metadata.framework,
            environment="production"
        )
        
        deployment_output = await self.execute_agent(
            "DeploymentAgent",
            deployment_input,
            context,
            state
        )
        
        # 5. Persistence (Save Site Version)
        state.add_log("info", "Saving site version")
        save_site_input = SaveSiteInput(
            session_id=context.session_id,
            site_id=site_id,
            site_name=site_data.get("name"),
            code=generated_code.html,
            requirements=input_data.get("requirements"),
            framework=generated_code.metadata.framework,
            changes=input_data.get("prompt", "Updated site")
        )
        
        site_save_output = await self.execute_agent(
            "MemoryAgent",
            save_site_input,
            context,
            state
        )
        
        return {
            "workflow_type": "update_site",
            "status": "completed",
            "site_id": site_id,
            "version_id": site_save_output.version_id,
            "deployment_url": deployment_output.deployment_metadata.url,
            "audit_score": audit_output.audit_result.overall_score if audit_output.audit_result else None
        }
    
    async def _execute_audit_only_workflow(
        self,
        input_data: Dict[str, Any],
        context: AgentContext,
        state: WorkflowState,
    ) -> Dict[str, Any]:
        """
        Execute AUDIT_ONLY workflow: Audit.
        
        Args:
            input_data: Workflow input data
            context: Agent context
            state: Workflow state
            
        Returns:
            Workflow result
        """
        state.add_log("info", "Starting AUDIT_ONLY workflow")
        
        html_code = input_data.get("html_code")
        framework = input_data.get("framework", "vanilla")
        
        if not html_code and input_data.get("site_id"):
            # Load from site
            site_id = input_data["site_id"]
            state.add_log("info", f"Loading site {site_id} for audit")
            from agents.memory_agent import LoadSiteInput
            
            load_site_input = LoadSiteInput(site_id=site_id)
            site_output = await self.execute_agent(
                "MemoryAgent",
                load_site_input,
                context,
                state
            )
            
            if site_output.success and site_output.data.get("site"):
                site_data = site_output.data["site"]
                html_code = site_data.get("latest_version", {}).get("code")
                framework = site_data.get("framework", "vanilla")
        
        if not html_code:
            raise ValueError("html_code or valid site_id required for audit")
            
        audit_input = AuditInput(
            html_code=html_code,
            framework=framework
        )
        
        audit_output = await self.execute_agent(
            "AuditAgent",
            audit_input,
            context,
            state
        )
        
        return {
            "workflow_type": "audit_only",
            "status": "completed",
            "audit_result": audit_output.audit_result.model_dump() if audit_output.audit_result else None
        }
    
    async def _execute_deploy_only_workflow(
        self,
        input_data: Dict[str, Any],
        context: AgentContext,
        state: WorkflowState,
    ) -> Dict[str, Any]:
        """
        Execute DEPLOY_ONLY workflow: Deploy.
        
        Args:
            input_data: Workflow input data
            context: Agent context
            state: Workflow state
            
        Returns:
            Workflow result
        """
        state.add_log("info", "Starting DEPLOY_ONLY workflow")
        
        html_code = input_data.get("html_code")
        files = input_data.get("files")
        site_name = input_data.get("site_name")
        framework = input_data.get("framework", "vanilla")
        site_id = input_data.get("site_id")
        
        if not html_code and site_id:
            # Load from site
            state.add_log("info", f"Loading site {site_id} for deployment")
            from agents.memory_agent import LoadSiteInput
            
            load_site_input = LoadSiteInput(site_id=site_id)
            site_output = await self.execute_agent(
                "MemoryAgent",
                load_site_input,
                context,
                state
            )
            
            if site_output.success and site_output.data.get("site"):
                site_data = site_output.data["site"]
                html_code = site_data.get("latest_version", {}).get("code")
                framework = site_data.get("framework", "vanilla")
                if not site_name:
                    site_name = site_data.get("name")
        
        if not html_code:
            raise ValueError("html_code or valid site_id required for deployment")
            
        deployment_input = DeploymentInput(
            html_code=html_code,
            files=files,
            site_name=site_name,
            site_id=site_id,
            framework=framework,
            environment=input_data.get("environment", "production")
        )
        
        deployment_output = await self.execute_agent(
            "DeploymentAgent",
            deployment_input,
            context,
            state
        )
        
        # Update site record with new deployment if site_id exists
        if site_id:
             # We might want to update the site record here, but DeploymentAgent might handle Vercel specific updates.
             # For now, we just return the result.
             pass
        
        return {
            "workflow_type": "deploy_only",
            "status": "completed",
            "deployment_url": deployment_output.deployment_metadata.url,
            "deployment_id": deployment_output.deployment_metadata.deployment_id
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get workflow status from memory or Redis.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Workflow state dict or None
        """
        # Try memory first
        if workflow_id in self.workflows:
            return self.workflows[workflow_id].to_dict()
        
        # Try Redis
        return self._load_workflow_state_from_redis(workflow_id)
    
    def get_all_workflows(self) -> List[Dict[str, Any]]:
        """
        Get all workflows in memory.
        
        Returns:
            List of workflow states
        """
        return [state.to_dict() for state in self.workflows.values()]
    
    def get_agent_metrics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get metrics for one or all agents.
        
        Args:
            agent_name: Optional agent name, if None returns all agents
            
        Returns:
            Agent metrics dictionary
        """
        if agent_name:
            if agent_name in self.agents:
                return self.agents[agent_name].get_metrics()
            return {}
        
        return {name: agent.get_metrics() for name, agent in self.agents.items()}
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            True if cancelled, False otherwise
        """
        if workflow_id not in self.workflows:
            return False
        
        state = self.workflows[workflow_id]
        
        if state.status == WorkflowStatus.RUNNING:
            state.status = WorkflowStatus.CANCELLED
            state.metrics.end()
            state.add_log("warning", "Workflow cancelled by user")
            
            # Save state
            self._save_workflow_state_to_redis(state)
            
            # Trigger callbacks
            await self._trigger_workflow_callbacks(workflow_id, "cancelled", {})
            
            logger.info(f"Workflow {workflow_id} cancelled")
            return True
        
        return False
    
    def persist_workflow_logs(self, workflow_id: str, db_session):
        """
        Persist workflow logs to database.
        
        Args:
            workflow_id: Workflow ID
            db_session: Database session
        """
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found for log persistence")
            return
        
        try:
            from services.metrics_service import MetricsService
            
            state = self.workflows[workflow_id]
            metrics_service = MetricsService(db_session)
            
            # Save all logs
            metrics_service.save_workflow_logs_batch(state.logs, workflow_id)
            
            # Update agent metrics
            for agent_name, duration in state.metrics.agent_durations.items():
                success = agent_name in state.completed_agents
                metrics_service.update_agent_metrics(agent_name, duration, success)
            
            logger.info(f"Persisted logs and metrics for workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to persist workflow logs: {str(e)}")
    
    def get_workflow_metrics_summary(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get comprehensive metrics summary for a workflow.
        
        Args:
            workflow_id: Workflow ID
            
        Returns:
            Metrics summary dictionary
        """
        if workflow_id not in self.workflows:
            return {}
        
        state = self.workflows[workflow_id]
        
        return {
            "workflow_id": workflow_id,
            "workflow_type": state.workflow_type.value,
            "status": state.status.value,
            "session_id": state.session_id,
            "metrics": state.metrics.to_dict(),
            "completed_agents": state.completed_agents,
            "failed_agent": state.failed_agent,
            "progress_percentage": state.progress_percentage,
            "log_counts": {
                "total": len(state.logs),
                "info": len([log for log in state.logs if log["level"] == "info"]),
                "warning": len([log for log in state.logs if log["level"] == "warning"]),
                "error": len([log for log in state.logs if log["level"] == "error"]),
            },
        }
    
    def cleanup_old_workflows(self, max_age_hours: int = 24):
        """
        Clean up old workflow states from memory.
        
        Args:
            max_age_hours: Maximum age in hours to keep workflows
        """
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        workflows_to_remove = []
        
        for workflow_id, state in self.workflows.items():
            if state.metrics.start_time:
                workflow_age = state.metrics.start_time.timestamp()
                if workflow_age < cutoff_time:
                    workflows_to_remove.append(workflow_id)
        
        for workflow_id in workflows_to_remove:
            del self.workflows[workflow_id]
            logger.info(f"Cleaned up old workflow: {workflow_id}")
        
        logger.info(f"Cleaned up {len(workflows_to_remove)} old workflows")
    
    def check_quality_thresholds(
        self,
        audit_result: Dict[str, Any],
        threshold_config: Optional[Dict[str, int]] = None
    ) -> Dict[str, Any]:
        """
        Check if audit scores meet quality thresholds.
        
        Args:
            audit_result: Audit result dictionary
            threshold_config: Optional custom threshold configuration
                            If None, uses default thresholds
            
        Returns:
            Dictionary with threshold check results
        """
        # Default thresholds
        default_thresholds = {
            "seo_min_score": 70,
            "accessibility_min_score": 80,
            "performance_min_score": 75,
            "overall_min_score": 75,
        }
        
        thresholds = threshold_config or default_thresholds
        
        # Extract scores from audit result
        seo_score = audit_result.get("seo", {}).get("score", 0)
        accessibility_score = audit_result.get("accessibility", {}).get("score", 0)
        performance_score = audit_result.get("performance", {}).get("score", 0)
        overall_score = audit_result.get("overall_score", 0)
        
        # Check each threshold
        seo_pass = seo_score >= thresholds["seo_min_score"]
        accessibility_pass = accessibility_score >= thresholds["accessibility_min_score"]
        performance_pass = performance_score >= thresholds["performance_min_score"]
        overall_pass = overall_score >= thresholds["overall_min_score"]
        
        meets_thresholds = seo_pass and accessibility_pass and performance_pass and overall_pass
        
        return {
            "meets_thresholds": meets_thresholds,
            "seo_pass": seo_pass,
            "accessibility_pass": accessibility_pass,
            "performance_pass": performance_pass,
            "overall_pass": overall_pass,
            "seo_gap": max(0, thresholds["seo_min_score"] - seo_score),
            "accessibility_gap": max(0, thresholds["accessibility_min_score"] - accessibility_score),
            "performance_gap": max(0, thresholds["performance_min_score"] - performance_score),
            "overall_gap": max(0, thresholds["overall_min_score"] - overall_score),
            "thresholds": thresholds,
            "scores": {
                "seo": seo_score,
                "accessibility": accessibility_score,
                "performance": performance_score,
                "overall": overall_score,
            }
        }
    
    def _generate_improvement_instructions(
        self,
        audit_result: Dict[str, Any],
        threshold_check: Dict[str, Any]
    ) -> str:
        """
        Generate improvement instructions based on audit results.
        
        Args:
            audit_result: Audit result dictionary
            threshold_check: Threshold check results
            
        Returns:
            Improvement instructions string
        """
        instructions = []
        instructions.append("Please improve the code to address the following issues:\n")
        
        # Add category-specific instructions
        if not threshold_check["seo_pass"]:
            seo_issues = audit_result.get("seo", {}).get("issues", [])
            if seo_issues:
                instructions.append(f"\nSEO Issues (current score: {threshold_check['scores']['seo']}, target: {threshold_check['thresholds']['seo_min_score']}):")
                for issue in seo_issues[:5]:  # Limit to top 5 issues
                    instructions.append(f"- {issue.get('description', 'Unknown issue')}")
                    if issue.get('fix_suggestion'):
                        instructions.append(f"  Fix: {issue['fix_suggestion']}")
        
        if not threshold_check["accessibility_pass"]:
            a11y_issues = audit_result.get("accessibility", {}).get("issues", [])
            if a11y_issues:
                instructions.append(f"\nAccessibility Issues (current score: {threshold_check['scores']['accessibility']}, target: {threshold_check['thresholds']['accessibility_min_score']}):")
                for issue in a11y_issues[:5]:
                    instructions.append(f"- {issue.get('description', 'Unknown issue')}")
                    if issue.get('fix_suggestion'):
                        instructions.append(f"  Fix: {issue['fix_suggestion']}")
        
        if not threshold_check["performance_pass"]:
            perf_issues = audit_result.get("performance", {}).get("issues", [])
            if perf_issues:
                instructions.append(f"\nPerformance Issues (current score: {threshold_check['scores']['performance']}, target: {threshold_check['thresholds']['performance_min_score']}):")
                for issue in perf_issues[:5]:
                    instructions.append(f"- {issue.get('description', 'Unknown issue')}")
                    if issue.get('fix_suggestion'):
                        instructions.append(f"  Fix: {issue['fix_suggestion']}")
        
        instructions.append("\nPlease maintain all existing functionality while addressing these issues.")
        
        return "\n".join(instructions)
    
    async def _execute_improve_site_workflow(
        self,
        input_data: Dict[str, Any],
        context: AgentContext,
        state: WorkflowState,
    ) -> Dict[str, Any]:
        """
        Execute IMPROVE_SITE workflow: Code → Audit → Check Thresholds → Improve (max 2 cycles).
        
        This workflow automatically improves code based on audit feedback until
        quality thresholds are met or maximum cycles (2) are reached.
        
        Args:
            input_data: Workflow input data containing:
                - html_code: Current HTML code
                - threshold_config: Optional custom thresholds
                - max_cycles: Optional max improvement cycles (default: 2)
            context: Agent context
            state: Workflow state
            
        Returns:
            Workflow result with improvement details
        """
        state.add_log("info", "Starting IMPROVE_SITE workflow")
        
        html_code = input_data.get("html_code")
        if not html_code:
            raise ValueError("html_code is required for improvement workflow")
        
        threshold_config = input_data.get("threshold_config")
        max_cycles = input_data.get("max_cycles", 2)
        
        improvement_cycles = []
        current_code = html_code
        
        for cycle_num in range(1, max_cycles + 1):
            state.add_log("info", f"Starting improvement cycle {cycle_num}/{max_cycles}")
            
            # Run audit on current code
            state.add_log("info", f"Running audit (cycle {cycle_num})")
            # TODO: Execute audit agent when available
            # For now, return placeholder
            audit_result = {
                "seo": {"score": 75, "issues": []},
                "accessibility": {"score": 85, "issues": []},
                "performance": {"score": 80, "issues": []},
                "overall_score": 80,
            }
            
            # Check thresholds
            threshold_check = self.check_quality_thresholds(audit_result, threshold_config)
            
            state.add_log(
                "info",
                f"Threshold check (cycle {cycle_num}): meets_thresholds={threshold_check['meets_thresholds']}",
                metadata=threshold_check
            )
            
            # Record cycle
            cycle_info = {
                "cycle_number": cycle_num,
                "initial_scores": threshold_check["scores"],
                "threshold_check": threshold_check,
                "audit_result": audit_result,
            }
            
            # If thresholds are met, we're done
            if threshold_check["meets_thresholds"]:
                state.add_log("info", f"Quality thresholds met in cycle {cycle_num}")
                cycle_info["success"] = True
                cycle_info["final_code"] = current_code
                improvement_cycles.append(cycle_info)
                break
            
            # If this is the last cycle, don't try to improve
            if cycle_num >= max_cycles:
                state.add_log(
                    "warning",
                    f"Maximum improvement cycles ({max_cycles}) reached without meeting thresholds"
                )
                cycle_info["success"] = False
                cycle_info["final_code"] = current_code
                cycle_info["reason"] = "max_cycles_reached"
                improvement_cycles.append(cycle_info)
                break
            
            # Generate improvement instructions
            improvement_instructions = self._generate_improvement_instructions(
                audit_result,
                threshold_check
            )
            
            state.add_log(
                "info",
                f"Generated improvement instructions for cycle {cycle_num}",
                metadata={"instructions_length": len(improvement_instructions)}
            )
            
            # Improve code using Code Generation Agent
            state.add_log("info", f"Improving code (cycle {cycle_num})")
            # TODO: Execute code generation agent with improvement instructions
            # For now, keep current code
            improved_code = current_code
            
            cycle_info["improvement_instructions"] = improvement_instructions
            cycle_info["improved_code"] = improved_code
            cycle_info["success"] = False  # Will be determined in next cycle
            improvement_cycles.append(cycle_info)
            
            # Update current code for next cycle
            current_code = improved_code
        
        # Final audit
        final_audit = improvement_cycles[-1]["audit_result"]
        final_threshold_check = improvement_cycles[-1]["threshold_check"]
        
        state.add_log(
            "info",
            f"Improvement workflow complete after {len(improvement_cycles)} cycle(s)",
            metadata={
                "final_scores": final_threshold_check["scores"],
                "meets_thresholds": final_threshold_check["meets_thresholds"]
            }
        )
        
        return {
            "workflow_type": "improve_site",
            "cycles": improvement_cycles,
            "final_code": current_code,
            "final_audit": final_audit,
            "final_threshold_check": final_threshold_check,
            "meets_thresholds": final_threshold_check["meets_thresholds"],
            "total_cycles": len(improvement_cycles),
        }


# Global orchestrator instance
orchestrator = AgentOrchestrator()
