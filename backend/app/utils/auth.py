from fastapi import Depends, HTTPException, status
from backend.app.models.user import UserSchema, UserRole
from backend.app.deps import get_current_user
import logging

def get_current_user():
    # Заглушка: всегда админ (реализовать OAuth/JWT при необходимости)
    return UserSchema(username="admin", role=UserRole.admin)

current_user_dependency = Depends(get_current_user)

def require_role(role: UserRole, user_dependency=current_user_dependency):
    def decorator(user: UserSchema = user_dependency):
        logging.info(f"require_role: user.role={user.role!r}, required={role!r}")
        if user.role != role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав")
        return user
    return decorator

admin_required = require_role(UserRole.admin, current_user_dependency) 