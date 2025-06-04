from backend.app.models.user import UserSchema, UserRole
from backend.app.core.database import get_db
from fastapi import Request, HTTPException, status
from types import SimpleNamespace

def get_current_user(request: Request):
    # Проверка заголовка X-User-Role для имитации авторизации
    role = request.headers.get("X-User-Role", "anonymous")
    user_id = int(request.headers.get("X-User-Id", "0"))
    username = request.headers.get("X-User-Name", "guest")
    if role == "admin":
        return SimpleNamespace(id=user_id or 1, username=username or "admin", role=UserRole.admin)
    elif role == "manager":
        return SimpleNamespace(id=user_id or 2, username=username or "manager", role=UserRole.manager)
    elif role == "user":
        return SimpleNamespace(id=user_id or 3, username=username or "user", role=UserRole.user)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

def get_current_active_user(request: Request):
    # Для совместимости с Depends(get_current_active_user)
    return get_current_user(request)