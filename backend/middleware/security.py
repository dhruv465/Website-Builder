"""
Security middleware for the FastAPI application.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

from utils.config import settings
from utils.logging import logger


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        if settings.ENVIRONMENT == "production":
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' wss: https:; "
                "frame-ancestors 'none';"
            )
            response.headers["Content-Security-Policy"] = csp
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.cleanup_interval = 60  # seconds
        self.last_cleanup = time.time()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # Try to get session ID first
        session_id = request.headers.get("X-Session-ID")
        if session_id:
            return f"session:{session_id}"
        
        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return f"ip:{forwarded.split(',')[0].strip()}"
        
        client_host = request.client.host if request.client else "unknown"
        return f"ip:{client_host}"
    
    def _cleanup_old_requests(self):
        """Remove old request records."""
        current_time = time.time()
        
        if current_time - self.last_cleanup > self.cleanup_interval:
            cutoff_time = current_time - 60
            
            for client_id in list(self.requests.keys()):
                self.requests[client_id] = [
                    req_time for req_time in self.requests[client_id]
                    if req_time > cutoff_time
                ]
                
                if not self.requests[client_id]:
                    del self.requests[client_id]
            
            self.last_cleanup = current_time
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_id(request)
        current_time = time.time()
        
        # Cleanup old requests periodically
        self._cleanup_old_requests()
        
        # Get requests in the last minute
        recent_requests = [
            req_time for req_time in self.requests[client_id]
            if req_time > current_time - 60
        ]
        
        # Check rate limit
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + 60))
                }
            )
        
        # Add current request
        self.requests[client_id].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(recent_requests) - 1
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(max(0, remaining))
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate incoming requests for security issues.
    """
    
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Check content length
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.MAX_CONTENT_LENGTH:
            logger.warning(f"Request too large: {content_length} bytes")
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={"detail": "Request body too large"}
            )
        
        # Validate content type for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            
            # Allow JSON and form data
            allowed_types = [
                "application/json",
                "application/x-www-form-urlencoded",
                "multipart/form-data"
            ]
            
            if not any(allowed in content_type for allowed in allowed_types):
                logger.warning(f"Invalid content type: {content_type}")
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={"detail": "Unsupported media type"}
                )
        
        # Check for suspicious patterns in URL
        suspicious_patterns = ["../", "..\\", "<script", "javascript:", "data:"]
        url_path = str(request.url.path).lower()
        
        if any(pattern in url_path for pattern in suspicious_patterns):
            logger.warning(f"Suspicious URL pattern detected: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": "Invalid request"}
            )
        
        return await call_next(request)


class SessionValidationMiddleware(BaseHTTPMiddleware):
    """
    Validate session IDs in requests.
    """
    
    # Paths that don't require session validation
    EXEMPT_PATHS = [
        "/health",
        "/",
        "/docs",
        "/openapi.json",
        "/api/sessions",  # Session creation endpoint
    ]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Skip validation for exempt paths
        if any(request.url.path.startswith(path) for path in self.EXEMPT_PATHS):
            return await call_next(request)
        
        # Get session ID from header
        session_id = request.headers.get("X-Session-ID")
        
        # For now, we just validate format (UUID)
        # In production, you'd validate against database
        if session_id:
            # Basic UUID format validation
            if len(session_id) != 36 or session_id.count("-") != 4:
                logger.warning(f"Invalid session ID format: {session_id}")
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid session"}
                )
        
        # Add session ID to request state for use in endpoints
        request.state.session_id = session_id
        
        return await call_next(request)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Log all requests and responses for security auditing.
    """
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "client": request.client.host if request.client else "unknown",
                "session_id": request.headers.get("X-Session-ID"),
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response: {response.status_code} ({duration:.3f}s)",
                extra={
                    "status_code": response.status_code,
                    "duration": duration,
                    "path": request.url.path,
                }
            )
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"Request failed: {str(e)} ({duration:.3f}s)",
                extra={
                    "error": str(e),
                    "duration": duration,
                    "path": request.url.path,
                }
            )
            raise


def setup_security_middleware(app):
    """
    Set up all security middleware for the application.
    """
    # Add middleware in reverse order (last added is executed first)
    
    # Logging (outermost - logs everything)
    app.add_middleware(LoggingMiddleware)
    
    # Security headers
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Rate limiting
    rate_limit = 100 if settings.ENVIRONMENT == "production" else 1000
    app.add_middleware(RateLimitMiddleware, requests_per_minute=rate_limit)
    
    # Request validation
    app.add_middleware(RequestValidationMiddleware)
    
    # Session validation (innermost - closest to route handlers)
    app.add_middleware(SessionValidationMiddleware)
    
    logger.info("Security middleware configured")
