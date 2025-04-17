from backend.app.models.user import UserSchema, UserRole

def get_current_user():
    # Заглушка: всегда админ (реализовать OAuth/JWT при необходимости)
    return UserSchema(username="admin", role=UserRole.admin) 