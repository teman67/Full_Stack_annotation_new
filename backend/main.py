from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from app.core.config import settings
from app.core.database_supabase import get_db_service, DatabaseService
from app.core.security import verify_token
# Remove SQLAlchemy imports - we're using Supabase only
from app.api.auth_supabase import router as auth_router
# We'll update these other routers to use Supabase too
# from app.api.projects import router as projects_router
# from app.api.documents import router as documents_router
# from app.api.annotations import router as annotations_router
# from app.api.admin import router as admin_router

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="FastAPI backend for Scientific Text Annotator - Supabase Edition",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_service = Depends(get_db_service)
):
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    user_id = payload.get("user_id")
    if email is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from Supabase
    user = db_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user

async def get_admin_user(
    current_user = Depends(get_current_user)
):
    """Dependency to ensure user is admin"""
    if not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])

# New Supabase-only routers (require email verification)
from app.api.projects_supabase import router as projects_supabase_router
app.include_router(projects_supabase_router, prefix="/api/projects", tags=["projects"])

# TODO: Update these routers to use Supabase
# app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
# app.include_router(annotations_router, prefix="/api/annotations", tags=["annotations"])
# app.include_router(admin_router, prefix="/api/admin", tags=["admin"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Scientific Text Annotator API",
        "version": settings.version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
