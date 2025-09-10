import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import get_session_local, get_engine
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.models.user import UserRole
from app.core.password_security import password_service

def create_admin():
    # Initialize the database engine and session
    engine = get_engine()
    SessionLocal = get_session_local()
    
    db = SessionLocal()
    try:
        user_service = UserService(db)
        # Проверка: есть ли уже админ
        admins = [u for u in user_service.get_users() if getattr(u, 'role', None) == UserRole.admin]
        if admins:
            admin = admins[0]
            print(f"Администратор уже существует: {admin.username} ({admin.email})")
            print("Повторное создание невозможно.")
            return
            
        # Test a password without sequential numbers
        password = "SecurePass!97531"  # No sequential numbers
        is_valid, errors = password_service.validate_password(password, "admin")
        print(f"Password validation: {is_valid}")
        print(f"Errors: {errors}")
        
        # Check for sequential characters
        has_seq = password_service._has_sequential_chars(password)
        print(f"Has sequential chars: {has_seq}")
        
        if not is_valid:
            print("Trying a different password...")
            # Try another password
            password = "PhStudio!9A8B7C"
            is_valid, errors = password_service.validate_password(password, "admin")
            print(f"Second password validation: {is_valid}")
            print(f"Errors: {errors}")
            
            if not is_valid:
                print("Trying a third password...")
                # Try a third password
                password = "StudioPass!A9B8C7"
                is_valid, errors = password_service.validate_password(password, "admin")
                print(f"Third password validation: {is_valid}")
                print(f"Errors: {errors}")
                
                if not is_valid:
                    print("All password attempts failed. Please check the password validation rules.")
                    return
        
        # Create admin user with known credentials that pass all validation rules
        admin = UserCreate(
            username="admin",
            email="admin@example.com",
            password=password,
            role=UserRole.admin,
            full_name="Admin User"
        )
        user_service.create_user(admin)
        print(f"Администратор успешно создан: {admin.username} ({admin.email})")
        print(f"Пароль: {password}")
    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()