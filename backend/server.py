"""Main FastAPI Application"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import logging
import json
from datetime import datetime, timezone
import time

from app.core.config import settings
from app.database.base import db_adapter
from app.routes import (
    auth_router,
    user_router,
    student_router,
    teacher_router,
    class_router,
    subject_router,
    attendance_router,
    grade_router,
    finance_router,
    dormitory_router,
    library_router,
    admin_router
)

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(message)s' if settings.LOG_FORMAT == 'json' else '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_data)


if settings.LOG_FORMAT == 'json':
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.root.handlers = [handler]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: {settings.DATABASE_TYPE}")
    
    try:
        await db_adapter.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await db_adapter.disconnect()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Comprehensive School Management System API",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan
)


# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware: Request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    duration = time.time() - start_time
    log_data = {
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "client_ip": request.client.host if request.client else None
    }
    
    if settings.LOG_FORMAT == 'json':
        logger.info(json.dumps(log_data))
    else:
        logger.info(f"{log_data['method']} {log_data['path']} - {log_data['status_code']} - {log_data['duration_ms']}ms")
    
    return response


# Middleware: Security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An unexpected error occurred"
        }
    )


# Health check endpoints
@app.get(f"{settings.API_PREFIX}/health", tags=["Health"])
async def health_check():
    """Health check endpoint (liveness)"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV
    }


@app.get(f"{settings.API_PREFIX}/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint"""
    checks = {
        "database": "healthy",
        "storage": "healthy",
        "cache": "healthy"
    }
    
    # TODO: Add actual health checks for each service
    
    all_healthy = all(v == "healthy" for v in checks.values())
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get(settings.API_PREFIX, tags=["Root"])
async def root():
    """API root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "health": f"{settings.API_PREFIX}/health"
    }


# Include routers
app.include_router(auth_router, prefix=settings.API_PREFIX, tags=["Authentication"])
app.include_router(user_router, prefix=settings.API_PREFIX, tags=["Users"])
app.include_router(student_router, prefix=settings.API_PREFIX, tags=["Students"])
app.include_router(teacher_router, prefix=settings.API_PREFIX, tags=["Teachers"])
app.include_router(class_router, prefix=settings.API_PREFIX, tags=["Classes"])
app.include_router(subject_router, prefix=settings.API_PREFIX, tags=["Subjects"])
app.include_router(attendance_router, prefix=settings.API_PREFIX, tags=["Attendance"])
app.include_router(grade_router, prefix=settings.API_PREFIX, tags=["Grades"])
app.include_router(finance_router, prefix=settings.API_PREFIX, tags=["Finance"])
app.include_router(dormitory_router, prefix=settings.API_PREFIX, tags=["Dormitory"])
app.include_router(library_router, prefix=settings.API_PREFIX, tags=["Library"])
app.include_router(admin_router, prefix=settings.API_PREFIX, tags=["Administration"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )