from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from ..models.base import Base
from .config import get_settings
import logging

logger = logging.getLogger(__name__)

# Global engine and session instances
engine = None
SessionLocal = None

def get_engine():
    """Get or create SQLAlchemy engine with PostgreSQL optimizations"""
    global engine
    if engine is None:
        settings = get_settings()
        
        # Use test database URL if in testing environment
        database_url = (
            settings.TEST_DATABASE_URL if settings.IS_TESTING 
            else settings.DATABASE_URL
        )
        
        engine_kwargs = {
            "echo": settings.ENV == "development",
            "poolclass": QueuePool,
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_POOL_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_recycle": settings.DB_POOL_RECYCLE,
            "pool_pre_ping": True,  # Validates connections before use
        }
        
        # PostgreSQL-specific settings
        if database_url.startswith("postgresql"):
            engine_kwargs.update({
                "connect_args": {
                    "connect_timeout": 10,
                    "application_name": "phstudio_app",
                    "options": "-c timezone=UTC"
                }
            })
        
        engine = create_engine(database_url, **engine_kwargs)
        
        # Add connection event listeners for PostgreSQL
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            # This is for PostgreSQL connection optimization
            if hasattr(dbapi_connection, 'autocommit'):
                dbapi_connection.autocommit = False
                
        logger.info(f"Database engine created for environment: {settings.ENV}")
    
    return engine

def get_session_local():
    """Get or create SessionLocal class"""
    global SessionLocal
    if SessionLocal is None:
        SessionLocal = sessionmaker(
            autocommit=False, 
            autoflush=False, 
            bind=get_engine()
        )
    return SessionLocal

def get_db():
    """Dependency for getting database session"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=get_engine())
    logger.info("Database tables initialized")

def health_check():
    """Check database connectivity"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
