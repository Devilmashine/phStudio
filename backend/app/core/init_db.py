from .database import engine, Base
from ..models.booking import Booking
from ..models.user import User

def init_db():
    """Инициализация базы данных"""
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("База данных успешно инициализирована") 