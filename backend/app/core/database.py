from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.core.config import settings
from supabase import create_client, Client
from fastapi import HTTPException

# Supabase client setup
supabase: Client = create_client(settings.supabase_url, settings.supabase_anon_key)

# Database URL construction for Supabase
def get_supabase_db_url():
    """Construct database URL from Supabase settings"""
    if settings.database_url:
        return settings.database_url
    
    # Extract database info from Supabase URL if needed
    # Supabase format: postgresql://[user[:password]@][netloc][:port][,...][/dbname]
    # This would be your Supabase connection string
    return f"postgresql://postgres:[YOUR_PASSWORD]@db.[YOUR_PROJECT_REF].supabase.co:5432/postgres"

# Only create engine if database_url is properly configured
engine = None
SessionLocal = None
async_engine = None
AsyncSessionLocal = None

try:
    # Try to create database connection
    db_url = get_supabase_db_url()
    print(f"Attempting database connection to: {db_url[:50]}...")
    
    # Test connection first
    test_engine = create_engine(
        db_url,
        pool_pre_ping=True,
        echo=False,  # Reduce noise during connection test
        connect_args={"connect_timeout": 5}  # Shorter timeout for test
    )
    
    # Test the connection
    with test_engine.connect() as conn:
        conn.execute("SELECT 1")
    
    # If test succeeds, create actual engine
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        echo=settings.debug,
        connect_args={"connect_timeout": 10}
    )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Async database setup (for FastAPI)
    async_engine = create_async_engine(
        db_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.debug
    )

    AsyncSessionLocal = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    print("✅ Database connection configured successfully")
    
except Exception as e:
    print(f"⚠️ Database connection error: {e}")
    print("🔄 Falling back to Supabase client for database operations")
    print("   This is actually a more robust approach for Supabase!")
    
    # Clean up test engine if it was created
    if 'test_engine' in locals():
        test_engine.dispose()
    SessionLocal = None
    async_engine = None
    AsyncSessionLocal = None

Base = declarative_base()

# Dependency to get database session
def get_db():
    """Database session dependency - uses SQLAlchemy if available, otherwise returns None"""
    if SessionLocal is None:
        # Return None to indicate that Supabase client should be used instead
        return None
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get Supabase client
def get_supabase_client():
    """Get Supabase client instance"""
    return supabase

# Dependency to get database adapter (Supabase or SQLAlchemy)
def get_db_adapter():
    """Get appropriate database adapter"""
    if SessionLocal is not None:
        # Use SQLAlchemy if available
        return get_db()
    else:
        # Use Supabase client adapter
        from app.core.supabase_adapter import get_supabase_adapter
        return get_supabase_adapter()

# Async dependency to get database session
async def get_async_db():
    """Async database session dependency"""
    if AsyncSessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Database not available. Please configure your Supabase connection."
        )
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Supabase helper functions
def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    return supabase
