from sqlalchemy import Column, Integer, String, Enum as SAEnum, DateTime, Index
from datetime import datetime, timezone
from .base import Base
from enum import Enum
from pydantic import BaseModel


class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    manager = "manager"


class UserSchema(BaseModel):
    username: str
    role: UserRole


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("idx_users_username", "username"),
        Index("idx_users_email", "email"),
        Index("idx_users_role", "role"),
        Index("idx_users_ical_token", "ical_token"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SAEnum(UserRole), nullable=False, default=UserRole.user)
    full_name = Column(String(200), nullable=True)
    
    # Use proper DateTime columns for PostgreSQL
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # iCal token for calendar integration
    ical_token = Column(String(64), unique=True, nullable=True)
    
    # Additional user properties for photo studio
    is_active = Column(String(5), default="true", nullable=False)
    phone = Column(String(20), nullable=True)
