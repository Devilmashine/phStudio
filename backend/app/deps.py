from app.models.user import UserSchema, UserRole, User
from app.core.database import get_db
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
from types import SimpleNamespace

# Import additional dependencies
from app.core.config import get_settings
from app.services.user import UserService

# Import employee dependencies
from app.models.employee_enhanced import Employee, EmployeeRole
from app.repositories.employee_repository import EmployeeRepository

# OAuth2 scheme for JWT token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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


def get_current_active_user(request: Request):
    # Для совместимости с Depends(get_current_active_user)
    return get_current_user(request)


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


# Employee authentication dependencies
async def get_current_employee(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current employee from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        settings = get_settings()
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        role: Optional[str] = payload.get("role")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Get employee from repository
    employee_repo = EmployeeRepository(db)
    employee = employee_repo.get_by_username(username)
    if employee is None:
        raise credentials_exception
    
    # Check if employee is active
    if employee.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee account is not active"
        )
    
    return employee


async def get_current_active_employee(employee: Employee = Depends(get_current_employee)):
    """Get current active employee"""
    if employee.status.value != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee account is not active"
        )
    return employee


async def get_current_employee_admin(employee: Employee = Depends(get_current_employee)):
    """Get current employee with admin privileges"""
    if employee.role != EmployeeRole.ADMIN and employee.role != EmployeeRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    return employee


async def get_current_employee_manager(employee: Employee = Depends(get_current_employee)):
    """Get current employee with manager or admin privileges"""
    if employee.role not in [EmployeeRole.ADMIN, EmployeeRole.OWNER, EmployeeRole.MANAGER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient privileges"
        )
    return employee