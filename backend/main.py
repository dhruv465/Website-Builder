"""
FastAPI application entry point for Smart Website Builder.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from utils.config import settings
from utils.logging import setup_logging, logger
from api import workflows, requirements, code, audit, deploy, sessions, integrations, improve, websocket, templates, assets, editing, forms, seo, export, billing
from middleware.security import setup_security_middleware
from middleware.rate_limit import setup_rate_limiting
from starlette.middleware.base import BaseHTTPMiddleware

# Setup logging
setup_logging()

class CSPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; connect-src 'self' ws: wss: https:;"
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Smart Website Builder API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    logger.info("Shutting down Smart Website Builder API")


# Create FastAPI application
app = FastAPI(
    title="Smart Website Builder API",
    description="Multi-agent AI system for creating, auditing, and deploying websites",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-Session-ID", "X-Request-ID"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
    max_age=3600,
)

# Setup security middleware
setup_security_middleware(app)

# Add CSP middleware
app.add_middleware(CSPMiddleware)

# Setup rate limiting
setup_rate_limiting(app)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
        }
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Smart Website Builder API",
        "docs": "/docs",
        "health": "/health",
    }


# Include routers
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(requirements.router, prefix="/api/requirements", tags=["Requirements"])
app.include_router(code.router, prefix="/api/code", tags=["Code Generation"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit"])
app.include_router(deploy.router, prefix="/api/deploy", tags=["Deployment"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(templates.router, prefix="/api", tags=["Templates"])
app.include_router(assets.router, prefix="/api", tags=["Assets"])
app.include_router(editing.router, prefix="/api/edit", tags=["Editing"])
app.include_router(forms.router, prefix="/api", tags=["Forms"])
app.include_router(seo.router, prefix="/api/seo", tags=["SEO"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])
app.include_router(billing.router, tags=["Billing"])
app.include_router(improve.router, tags=["Improvement"])
app.include_router(websocket.router, tags=["WebSocket"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
    )
