from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from typing import List, Optional
import logging

from ...core.database import get_db
from ...services.user import UserService
from ...schemas.user import UserCreate, UserResponse, UserUpdate
from ...models.user import User, UserRole
from ...core.config import get_settings, Settings
from fastapi.responses import JSONResponse
from fastapi import Response, Cookie

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Функции для работы с JWT токенами
def create_access_token(data: dict, settings: Settings = Depends(get_settings)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, settings: Settings = Depends(get_settings)):
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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверные учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
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


@router.post("/token")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name}, settings=settings
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role.name}, settings=settings
    )
    response = JSONResponse({"access_token": access_token, "token_type": "bearer"})
    set_refresh_cookie(response, refresh_token)
    # Аудит входа
    logger.info(
        f"LOGIN: user={user.username}, ip=TODO, time={datetime.now(timezone.utc)}"
    )
    return response


@router.post("/refresh")
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token отсутствует")
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401, detail="Недействительный refresh token"
            )
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if username is None or role is None:
            raise HTTPException(
                status_code=401, detail="Недействительный refresh token"
            )
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный refresh token")
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None or user.role.name != role:
        raise HTTPException(
            status_code=401, detail="Пользователь не найден или роль изменилась"
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.name}, settings=settings
    )
    set_refresh_cookie(response, refresh_token)  # продлеваем cookie
    # Аудит refresh
    logger.info(
        f"REFRESH: user={user.username}, ip=TODO, time={datetime.now(timezone.utc)}"
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    clear_refresh_cookie(response)
    # Аудит выхода
    logger.info(f"LOGOUT: ip=TODO, time={datetime.now(timezone.utc)}")
    return {"detail": "Выход выполнен"}


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


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user_service = UserService(db)
    return user_service.delete_user(user_id)
