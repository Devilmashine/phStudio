from backend.app.core.database import engine, Base
from backend.app.models.booking import Booking
from backend.app.models.user import User

def init_db():
    """Инициализация базы данных"""
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("База данных успешно инициализирована") 