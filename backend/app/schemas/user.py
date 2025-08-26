from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    ical_token: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: int
    created_at: str
    last_login: Optional[str] = None

    class ConfigDict:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    detail: str


class SecurityStats(BaseModel):
    total_users: int
    active_users: int
    locked_accounts: int
    failed_login_attempts_today: int


class PasswordValidation(BaseModel):
    is_valid: bool
    errors: list[str]
    strength: str
    score: int


class GeneratedPassword(BaseModel):
    password: str
    strength: str
    score: int
    is_valid: bool
