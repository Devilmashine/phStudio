import os
from sqlalchemy import create_engine
from alembic.config import Config
from alembic import command

def setup_test_database():
    """
    Создает тестовую базу данных в памяти и применяет к ней миграции.
    """
    db_url = "sqlite:///:memory:"
    os.environ["DATABASE_URL"] = db_url

    engine = create_engine(db_url)

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "backend/migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    with engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")

    return engine

if __name__ == "__main__":
    setup_test_database()
    print("Test database created and migrations applied.")
