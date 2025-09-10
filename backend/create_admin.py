import sys
import getpass
import re
import secrets
from app.core.database import get_session_local, get_engine
from app.services.user import UserService
from app.schemas.user import UserCreate
from app.models.user import UserRole

def validate_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

def validate_username(username: str) -> bool:
    return re.match(r"^[A-Za-z0-9_\-.]{3,32}$", username) is not None

def validate_password(password: str) -> bool:
    return len(password) >= 8

def prompt_admin_data():
    print("\n=== Создание первого администратора ===")
    print("Если администратор уже существует, повторное создание невозможно.\n")
    username = input("Логин (от 3 до 32 символов, латиница/цифры/._-): ").strip()
    if not validate_username(username):
        print("Некорректный логин. Допустимы латиница, цифры, . _ -, длина 3-32.")
        sys.exit(1)
    email = input("Email: ").strip()
    if not validate_email(email):
        print("Некорректный email.")
        sys.exit(1)
    gen = input("Сгенерировать случайный пароль? [y/N]: ").strip().lower()
    if gen == 'y':
        password = secrets.token_urlsafe(12)
        print(f"Сгенерированный пароль: {password}")
    else:
        password = getpass.getpass("Пароль (мин. 8 символов): ")
        password2 = getpass.getpass("Повторите пароль: ")
        if password != password2:
            print("Пароли не совпадают.")
            sys.exit(1)
        if not validate_password(password):
            print("Пароль слишком короткий (мин. 8 символов).")
            sys.exit(1)
    full_name = input("Имя (опционально): ").strip() or "Администратор"
    return username, email, password, full_name

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
            print("Повторное создание невозможно. Если забыли пароль — сбросьте его через БД.")
            return
        username, email, password, full_name = prompt_admin_data()
        admin = UserCreate(
            username=username,
            email=email,
            password=password,
            role=UserRole.admin,
            full_name=full_name
        )
        user_service.create_user(admin)
        print(f"Администратор успешно создан: {username} ({email})")
    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
        raise
    finally:
        db.close()

def print_usage():
    print("""
Скрипт для создания первого администратора.
- Если админ уже есть, повторное создание невозможно (idempotency).
- Пароль можно ввести вручную (не отображается) или сгенерировать автоматически.
- Логин/email/пароль проходят базовую валидацию.
- Для сброса пароля используйте отдельный скрипт или вручную в БД.

Запуск:
    python backend/create_admin.py
""")

if __name__ == "__main__":
    print_usage()
    create_admin()