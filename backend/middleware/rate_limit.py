from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response

# Initialize limiter with remote address as key
limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    """Configure rate limiting for the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Define standard limits
class RateLimits:
    STANDARD = "100/minute"
    AI_GENERATION = "10/minute"
    AUTH = "5/minute"
    SENSITIVE = "3/minute"
