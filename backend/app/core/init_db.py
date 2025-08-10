from .database import engine, Base


def init_db():
    """Инициализация базы данных"""
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine)
    print("База данных успешно инициализирована")
