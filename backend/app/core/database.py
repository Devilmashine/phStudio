from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.base import Base
from .config import get_settings

def get_engine():
    settings = get_settings()
    return create_engine(settings.DATABASE_URL)

def get_session_local():
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db():
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
