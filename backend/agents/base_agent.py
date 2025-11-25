"""
Base agent class and common models for all agents.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """Types of errors that can occur in agents."""
    VALIDATION_ERROR = "validation_error"
    LLM_ERROR = "llm_error"
    NETWORK_ERROR = "network_error"
    DEPLOYMENT_ERROR = "deployment_error"
    STORAGE_ERROR = "storage_error"
    TIMEOUT_ERROR = "timeout_error"
    UNKNOWN_ERROR = "unknown_error"


class AgentError(Exception):
    """Custom exception for agent errors."""
    
    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        agent_name: str,
        recoverable: bool = False,
        retryable: bool = False,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.agent_name = agent_name
        self.recoverable = recoverable
        self.retryable = retryable
        self.context = context or {}
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary."""
        return {
            "message": self.message,
            "error_type": self.error_type.value,
            "agent_name": self.agent_name,
            "recoverable": self.recoverable,
            "retryable": self.retryable,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


class ValidationResult(BaseModel):
    """Result of validation operation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)


class AgentInput(BaseModel):
    """Base input model for all agents."""
    request_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "allow"


class AgentOutput(BaseModel):
    """Base output model for all agents."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    validation_result: Optional[ValidationResult] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    execution_time: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        extra = "allow"


class AgentContext(BaseModel):
    """Context passed between agents during workflow execution."""
    session_id: str
    workflow_id: str
    previous_outputs: Dict[str, Any] = Field(default_factory=dict)
    user_preferences: Dict[str, Any] = Field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def add_output(self, agent_name: str, output: Any):
        """Add agent output to context."""
        self.previous_outputs[agent_name] = output
    
    def get_output(self, agent_name: str) -> Optional[Any]:
        """Get output from a previous agent."""
        return self.previous_outputs.get(agent_name)
    
    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
    
    def can_retry(self) -> bool:
        """Check if retry is allowed."""
        return self.retry_count < self.max_retries


class AgentMetrics(BaseModel):
    """Metrics for agent performance tracking."""
    agent_name: str
    execution_count: int = 0
    success_count: int = 0
    error_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    last_execution_time: Optional[datetime] = None
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    
    def record_execution(self, execution_time: float, success: bool, error: Optional[str] = None):
        """Record an execution."""
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.average_execution_time = self.total_execution_time / self.execution_count
        self.last_execution_time = datetime.utcnow()
        
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            self.last_error = error
            self.last_error_time = datetime.utcnow()
    
    def get_success_rate(self) -> float:
        """Calculate success rate."""
        if self.execution_count == 0:
            return 0.0
        return self.success_count / self.execution_count
    
    def get_error_rate(self) -> float:
        """Calculate error rate."""
        if self.execution_count == 0:
            return 0.0
        return self.error_count / self.execution_count


class BaseAgent(ABC):
    """
    Base class for all agents in the Smart Website Builder.
    
    All agents must inherit from this class and implement the abstract methods.
    """
    
    def __init__(self, name: str):
        """
        Initialize the agent.
        
        Args:
            name: Name of the agent
        """
        self.name = name
        self.metrics = AgentMetrics(agent_name=name)
    
    @abstractmethod
    async def execute(self, input_data: AgentInput, context: AgentContext) -> AgentOutput:
        """
        Execute the agent's main logic.
        
        Args:
            input_data: Input data for the agent
            context: Execution context with workflow state
            
        Returns:
            AgentOutput with results
            
        Raises:
            AgentError: If execution fails
        """
        pass
    
    @abstractmethod
    def validate(self, output: AgentOutput) -> ValidationResult:
        """
        Validate the agent's output.
        
        Args:
            output: Output to validate
            
        Returns:
            ValidationResult with validation status
        """
        pass
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics.model_dump()
    
    async def execute_with_metrics(
        self,
        input_data: AgentInput,
        context: AgentContext,
    ) -> AgentOutput:
        """
        Execute agent with automatic metrics tracking.
        
        Args:
            input_data: Input data for the agent
            context: Execution context
            
        Returns:
            AgentOutput with results
        """
        start_time = datetime.utcnow()
        success = False
        error_message = None
        
        try:
            output = await self.execute(input_data, context)
            success = output.success
            
            # Validate output
            validation_result = self.validate(output)
            output.validation_result = validation_result
            
            if not validation_result.is_valid:
                success = False
                error_message = "; ".join(validation_result.errors)
            
            return output
            
        except AgentError as e:
            success = False
            error_message = e.message
            raise
            
        except Exception as e:
            success = False
            error_message = str(e)
            raise AgentError(
                message=f"Unexpected error in {self.name}: {str(e)}",
                error_type=ErrorType.UNKNOWN_ERROR,
                agent_name=self.name,
                recoverable=False,
                retryable=False,
            )
            
        finally:
            # Record metrics
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds()
            self.metrics.record_execution(execution_time, success, error_message)
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}')"
