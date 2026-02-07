"""
Main FastAPI application - Cosmic Watch Backend
"""
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime

from app.core.config import settings
from app.core.database import init_db, Base, engine, SessionLocal
from app.routes import auth, asteroids, watchlist, alerts, chat

# Initialize database tables
init_db()

# Seed sample data if database is empty (demo user only)
db = SessionLocal()
try:
    from app.models.models import User
    existing_user = db.query(User).filter(User.email == "demo@cosmicwatch.io").first()
    if not existing_user:
        from app.core.security import hash_password
        demo_user = User(
            email="demo@cosmicwatch.io",
            username="demo",
            password_hash=hash_password("Demo@12345"),
            is_active=True
        )
        db.add(demo_user)
        db.commit()
finally:
    db.close()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Monitor Near-Earth Objects with AI-powered risk insights",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# ============ MIDDLEWARE ============

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware (security)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.cosmicwatch.io"]
)

# ============ ROUTE REGISTRATION ============

app.include_router(auth.router)
app.include_router(asteroids.router)
app.include_router(watchlist.router)
app.include_router(alerts.router)
app.include_router(chat.router)

# ============ HEALTH CHECK ============

@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version
    }


@app.get("/", tags=["root"])
def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/api/docs",
        "message": "Welcome to Cosmic Watch - Monitor NEOs with AI insights"
    }

# ============ EXCEPTION HANDLERS ============

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat()
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
