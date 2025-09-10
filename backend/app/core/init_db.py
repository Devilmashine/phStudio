from .database import get_engine
from ..models.base import Base
from ..models.enhanced_base import EnhancedBase
import logging

logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    try:
        # Получаем engine
        engine = get_engine()
        if engine is None:
            logger.error("Failed to create database engine")
            return
            
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        EnhancedBase.metadata.create_all(bind=engine)
        print("База данных успешно инициализирована")
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise