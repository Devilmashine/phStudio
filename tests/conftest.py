import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.models.booking import BookingLegacy
from backend.app.models.calendar_event import CalendarEvent


@pytest.fixture
def db_session():
    """Provide a transactional session backed by an in-memory SQLite database."""
    engine = create_engine("sqlite:///:memory:", future=True)

    tables = [CalendarEvent.__table__, BookingLegacy.__table__]
    for table in tables:
        table.create(bind=engine)

    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        for table in reversed(tables):
            table.drop(bind=engine)
