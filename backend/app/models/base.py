from sqlalchemy.orm import declarative_base

# Базовый класс для всех моделей
# Все модели наследуются от этого класса
# Он импортирует Base из database.py

Base = declarative_base()