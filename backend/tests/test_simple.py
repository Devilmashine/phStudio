import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.employee import Employee
from app.models.booking import BookingLegacy

# Create in-memory SQLite database for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    # Create only specific tables for testing
    Employee.__table__.create(engine, checkfirst=True)
    BookingLegacy.__table__.create(engine, checkfirst=True)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_employee_model_creation(db_session):
    """Test creation of employee model"""
    employee = Employee(
        full_name="John Doe",
        position="Manager",
        email="john@example.com",
        phone="+1234567890"
    )
    
    db_session.add(employee)
    db_session.commit()
    
    assert employee.id is not None
    assert employee.full_name == "John Doe"
    assert employee.email == "john@example.com"

def test_booking_model_creation(db_session):
    """Test creation of booking model"""
    from datetime import datetime
    booking = BookingLegacy(
        client_name="Jane Smith",
        client_phone="+1234567890",
        phone_normalized="+1234567890",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_price=100.0
    )
    
    db_session.add(booking)
    db_session.commit()
    
    assert booking.id is not None
    assert booking.client_name == "Jane Smith"
    assert booking.client_phone == "+1234567890"
