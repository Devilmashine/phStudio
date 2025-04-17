from backend.app.core.database import SessionLocal
from backend.app.services.user import UserService
from backend.app.schemas.user import UserCreate
from backend.app.models.user import UserRole

def create_admin():
    db = SessionLocal()
    try:
        user_service = UserService(db)
        admin = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",  # В реальном проекте используйте сложный пароль
            role=UserRole.ADMIN,
            full_name="Администратор"
        )
        user_service.create_user(admin)
        print("Администратор успешно создан")
    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 