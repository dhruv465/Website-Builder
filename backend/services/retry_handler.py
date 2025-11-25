"""
Retry handler with exponential backoff for agent execution.
"""
import asyncio
import time
from typing import Any, Callable, Optional, TypeVar, Coroutine
from functools import wraps

from agents.base_agent import AgentError, ErrorType
from utils.logging import logger

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        """
        Initialize retry configuration.
        
        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            exponential_base: Base for exponential backoff
            jitter: Whether to add random jitter to delays
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """
        Calculate delay for a given attempt.
        
        Args:
            attempt: Attempt number (0-indexed)
            
        Returns:
            Delay in seconds
        """
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )
        
        if self.jitter:
            import random
            delay = delay * (0.5 + random.random())
        
        return delay


def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable.
    
    Args:
        error: Exception to check
        
    Returns:
        True if error is retryable
    """
    if isinstance(error, AgentError):
        return error.retryable
    
    # Network errors are generally retryable
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True
    
    # Other errors are not retryable by default
    return False


async def retry_with_backoff(
    func: Callable[..., Coroutine[Any, Any, T]],
    *args,
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
    **kwargs
) -> T:
    """
    Execute an async function with exponential backoff retry logic.
    
    Args:
        func: Async function to execute
        *args: Positional arguments for func
        config: Retry configuration
        on_retry: Optional callback called on each retry (attempt, error, delay)
        **kwargs: Keyword arguments for func
        
    Returns:
        Result from func
        
    Raises:
        Exception: Last exception if all retries fail
    """
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(config.max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            
            # Log success after retry
            if attempt > 0:
                logger.info(f"Operation succeeded after {attempt} retries")
            
            return result
            
        except Exception as e:
            last_exception = e
            
            # Check if we should retry
            if attempt >= config.max_retries:
                logger.error(f"Operation failed after {config.max_retries} retries: {str(e)}")
                raise
            
            if not is_retryable_error(e):
                logger.error(f"Non-retryable error encountered: {str(e)}")
                raise
            
            # Calculate delay
            delay = config.get_delay(attempt)
            
            logger.warning(
                f"Attempt {attempt + 1}/{config.max_retries + 1} failed: {str(e)}. "
                f"Retrying in {delay:.2f}s..."
            )
            
            # Call retry callback if provided
            if on_retry:
                on_retry(attempt, e, delay)
            
            # Wait before retry
            await asyncio.sleep(delay)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    raise RuntimeError("Retry logic failed unexpectedly")


def with_retry(config: Optional[RetryConfig] = None):
    """
    Decorator to add retry logic to async functions.
    
    Args:
        config: Retry configuration
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_with_backoff(func, *args, config=config, **kwargs)
        return wrapper
    return decorator
