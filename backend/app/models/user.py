from sqlalchemy import Column, Integer, String, Enum as SAEnum
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
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(SAEnum(UserRole), nullable=False)
    full_name = Column(String)
    created_at = Column(String, default=lambda: datetime.now(timezone.utc).isoformat())
    last_login = Column(String, nullable=True)
    ical_token = Column(String(64), unique=True, nullable=True)
