from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import List, Optional
import logging
from app.core.database import get_db
from app.services.user import UserService
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserLogin, TokenResponse, MessageResponse, SecurityStats, PasswordValidation, GeneratedPassword
from app.models.user import User, UserRole
from app.core.config import get_settings
from app.services.log_service import log_action

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request headers"""
    # Check for X-Forwarded-For header (common with proxies/load balancers)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Take the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    # Check for X-Real-IP header (used by nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fall back to client host
    return request.client.host if request.client else "unknown"


# Функции для работы с JWT токенами
def create_access_token(data: dict):
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict):
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def set_refresh_cookie(response: Response, refresh_token: str):
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Только через HTTPS в production
        samesite="lax",
        max_age=60 * 60 * 24 * 30,  # 30 дней
    )


def clear_refresh_cookie(response: Response):
    response.delete_cookie("refresh_token")


async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        settings = get_settings()
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    # Если роль в токене не совпадает с ролью в БД — считаем токен недействительным
    if role and user.role.name != role:
        raise credentials_exception
    return user


async def get_current_admin(current_user=Depends(get_current_user)):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
        )
    return current_user


async def get_current_manager(current_user=Depends(get_current_user)):
    if current_user.role not in [UserRole.admin, UserRole.manager]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав"
        )
    return current_user


@router.post("/token", response_model=TokenResponse)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    client_ip = get_client_ip(request)
    user_service = UserService(db)
    
    # Check account lockout before attempting authentication
    is_locked, unlock_time, remaining_attempts = user_service.check_account_lockout(
        form_data.username, client_ip
    )
    
    if is_locked:
        log_action(form_data.username, "LOGIN_BLOCKED", f"ip={client_ip},reason=account_locked")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account is temporarily locked. Try again after {unlock_time}",
            headers={
                "Retry-After": "1800",  # 30 minutes
                "X-Account-Locked-Until": unlock_time.isoformat() if unlock_time else ""
            },
        )
    
    try:
        user = user_service.authenticate_user(form_data.username, form_data.password, client_ip)
        if not user:
            # Get updated remaining attempts after failed login
            _, _, remaining = user_service.check_account_lockout(form_data.username, client_ip)
            
            log_action(form_data.username, "LOGIN_FAILED", f"ip={client_ip},remaining_attempts={remaining}")
            
            # Provide hint about remaining attempts without being too specific
            detail = "Неверное имя пользователя или пароль"
            if remaining <= 2:
                detail += f". Внимание: осталось {remaining} попыток до блокировки аккаунта"
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=detail,
                headers={
                    "WWW-Authenticate": "Bearer",
                    "X-Remaining-Attempts": str(remaining)
                },
            )
    except HTTPException:
        # Re-raise HTTP exceptions (like account lockout)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during login for {form_data.username}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
    # Successful authentication - create tokens
    access_token = create_access_token(data={"sub": user.username, "role": user.role.name})
    refresh_token = create_refresh_token(data={"sub": user.username, "role": user.role.name})
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    set_refresh_cookie(response, refresh_token)
    
    # Enhanced security logging
    log_action(user.username, "LOGIN_SUCCESS", f"ip={client_ip},role={user.role.name}")
    logger.info(f"Successful login: {user.username} from {client_ip} at {datetime.now(timezone.utc)}")
    
    return response


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response, 
    refresh_token: Optional[str] = Cookie(None), 
    db: Session = Depends(get_db)
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token отсутствует")
    try:
        settings = get_settings()
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Недействительный refresh token")
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if username is None or role is None:
            raise HTTPException(status_code=401, detail="Недействительный refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None or user.role.name != role:
        raise HTTPException(status_code=401, detail="Пользователь не найден или роль изменилась")
    access_token = create_access_token(data={"sub": user.username, "role": user.role.name})
    set_refresh_cookie(response, refresh_token)  # продлеваем cookie
    
    # Structured audit logging
    client_ip = get_client_ip(request)
    log_action(user.username, "REFRESH_TOKEN", f"ip={client_ip}")
    logger.info(f"Token refreshed for user {user.username} from {client_ip} at {datetime.now(timezone.utc)}")
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, response: Response):
    clear_refresh_cookie(response)
    
    # Structured audit logging
    client_ip = get_client_ip(request)
    log_action("unknown", "LOGOUT", f"ip={client_ip}")
    logger.info(f"User logged out from {client_ip} at {datetime.now(timezone.utc)}")
    
    return {"detail": "Выход выполнен"}


@router.get("/security/stats", response_model=SecurityStats)
async def get_security_stats(
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get security statistics (admin only)"""
    user_service = UserService(db)
    stats = user_service.get_security_stats()
    return stats


@router.post("/security/unlock-account", response_model=MessageResponse)
async def unlock_account(
    username: str,
    client_ip: str = "unknown",
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually unlock a user account (admin only)"""
    user_service = UserService(db)
    success = user_service.unlock_account(username, client_ip)
    
    if success:
        log_action(current_user.username, "UNLOCK_ACCOUNT", f"target={username},ip={client_ip}")
        return {"message": f"Account {username} has been unlocked"}
    else:
        return {"message": f"Account {username} was not locked or does not exist"}


@router.post("/security/validate-password", response_model=PasswordValidation)
async def validate_password(
    password: str,
    username: str = None,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Validate password strength (admin only)"""
    user_service = UserService(db)
    is_valid, errors, strength, score = user_service.validate_password_strength(password, username)
    
    return {
        "is_valid": is_valid,
        "errors": errors,
        "strength": strength,
        "score": score
    }


@router.post("/security/generate-password", response_model=GeneratedPassword)
async def generate_secure_password(
    length: int = 16,
    current_user=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Generate a secure password (admin only)"""
    user_service = UserService(db)
    password = user_service.generate_secure_password(length)
    
    # Validate the generated password
    is_valid, errors, strength, score = user_service.validate_password_strength(password)
    
    return {
        "password": password,
        "strength": strength,
        "score": score,
        "is_valid": is_valid
    }


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user_service = UserService(db)
    return user_service.create_user(user_data)


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager),
):
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)


@router.get("/users/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user_service = UserService(db)
    return user_service.update_user(user_id, user_data)


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user_service = UserService(db)
    return user_service.delete_user(user_id)
