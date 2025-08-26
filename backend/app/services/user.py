from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from passlib.context import CryptContext
from typing import Optional, List, Tuple
from secrets import token_urlsafe
import logging

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.password_security import password_service, account_security_service
from app.core.config import get_settings

# Enhanced password context with stronger settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Increased rounds for better security
)

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def create_user(self, user_data: UserCreate) -> User:
        # Check for existing users
        if self.get_user_by_username(user_data.username):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким именем уже существует"
            )
        if self.get_user_by_email(user_data.email):
            raise HTTPException(
                status_code=400, detail="Пользователь с таким email уже существует"
            )

        # Comprehensive password validation
        is_valid, password_errors = password_service.validate_password(
            user_data.password, user_data.username
        )
        if not is_valid:
            raise HTTPException(
                status_code=400, 
                detail=f"Password validation failed: {'; '.join(password_errors)}"
            )
        
        # Log password strength for monitoring
        strength, score = password_service.get_password_strength(user_data.password)
        logger.info(f"User {user_data.username} created with password strength: {strength} ({score}/100)")

        # Hash password with enhanced security
        hashed_password = pwd_context.hash(user_data.password)
        ical_token = token_urlsafe(32)
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            ical_token=ical_token,
            full_name=user_data.full_name,
        )

        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            # Log user creation for security audit
            logger.info(f"User created successfully: {user_data.username} ({user_data.email})")
            return db_user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database integrity error creating user {user_data.username}: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Ошибка при создании пользователя"
            )

    def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(
                update_data.pop("password")
            )

        for field, value in update_data.items():
            setattr(user, field, value)

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Ошибка при обновлении пользователя"
            )

    def delete_user(self, user_id: int) -> bool:
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        try:
            self.db.delete(user)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=400, detail="Ошибка при удалении пользователя"
            )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def authenticate_user(self, username: str, password: str, client_ip: str = "unknown") -> Optional[User]:
        """Enhanced authentication with account lockout protection"""
        identifier = f"{username}:{client_ip}"
        
        # Check if account is locked
        is_locked, unlock_time = account_security_service.is_locked(identifier)
        if is_locked:
            logger.warning(f"Login attempt for locked account: {username} from {client_ip}")
            raise HTTPException(
                status_code=429,
                detail=f"Account is locked due to too many failed attempts. Try again after {unlock_time}"
            )
        
        user = self.get_user_by_username(username)
        if not user:
            # Record failed attempt for non-existent user to prevent enumeration
            account_security_service.record_failed_login(identifier)
            logger.warning(f"Login attempt for non-existent user: {username} from {client_ip}")
            return None
        
        if not self.verify_password(password, user.hashed_password):
            # Record failed login attempt
            account_security_service.record_failed_login(identifier)
            remaining = account_security_service.get_remaining_attempts(identifier)
            logger.warning(f"Failed login attempt for {username} from {client_ip}. {remaining} attempts remaining")
            return None

        # Successful login
        account_security_service.record_successful_login(identifier)
        user.last_login = datetime.now(timezone.utc)
        
        try:
            self.db.commit()
            logger.info(f"Successful login: {username} from {client_ip}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Database error during login for {username}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def validate_password_strength(self, password: str, username: str = None) -> Tuple[bool, List[str], str, int]:
        """Validate password strength and return detailed analysis"""
        is_valid, errors = password_service.validate_password(password, username)
        strength, score = password_service.get_password_strength(password)
        return is_valid, errors, strength, score
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a cryptographically secure password"""
        return password_service.generate_secure_password(length)
    
    def check_account_lockout(self, username: str, client_ip: str = "unknown") -> Tuple[bool, Optional[datetime], int]:
        """Check if account is locked and return lockout info"""
        identifier = f"{username}:{client_ip}"
        is_locked, unlock_time = account_security_service.is_locked(identifier)
        remaining_attempts = account_security_service.get_remaining_attempts(identifier)
        return is_locked, unlock_time, remaining_attempts
    
    def unlock_account(self, username: str, client_ip: str = "unknown") -> bool:
        """Manually unlock an account (admin function)"""
        identifier = f"{username}:{client_ip}"
        if identifier in account_security_service.failed_attempts:
            del account_security_service.failed_attempts[identifier]
            logger.info(f"Account manually unlocked: {username} from {client_ip}")
            return True
        return False
    
    def get_security_stats(self) -> dict:
        """Get security statistics for monitoring"""
        locked_accounts = sum(1 for data in account_security_service.failed_attempts.values() 
                            if data.get('locked_until') and data['locked_until'] > datetime.utcnow())
        
        failed_attempts_count = len(account_security_service.failed_attempts)
        
        return {
            "locked_accounts": locked_accounts,
            "accounts_with_failed_attempts": failed_attempts_count,
            "total_users": self.db.query(User).count()
        }
