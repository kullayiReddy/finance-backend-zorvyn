"""
Finance Dashboard Backend - Main Application (Fixed Imports)
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config import settings
from database import init_db

# Import routes
import auth_routes
import user_routes
import record_routes
import dashboard_routes

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="A production-quality backend for Finance Data Processing with Role-Based Access Control",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(record_routes.router)
app.include_router(dashboard_routes.router)

# Health check endpoint
@app.get("/health", tags=["System"])
def health_check():
    """System health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

# Root endpoint
@app.get("/", tags=["System"])
def root():
    """API root endpoint with information"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "documentation": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# Global error handler for unhandled exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": str(exc) if settings.DEBUG else "Internal server error",
            "status_code": 500
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔════════════════════════════════════════════════════════╗
    ║       Finance Dashboard Backend Server Starting       ║
    ╠════════════════════════════════════════════════════════╣
    ║ App: {settings.APP_NAME:46} ║
    ║ Version: {settings.APP_VERSION:43} ║
    ║ Debug: {str(settings.DEBUG):48} ║
    ║ Database: {settings.DATABASE_URL:44} ║
    ╠════════════════════════════════════════════════════════╣
    ║ Swagger UI: http://localhost:8000/docs                ║
    ║ ReDoc: http://localhost:8000/redoc                    ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main_fixed:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
