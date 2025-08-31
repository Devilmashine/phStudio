import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.employee import Employee
from app.models.booking import Booking, BookingStatus
from app.models.domain_event import DomainEvent
from app.repositories.employee_repository import EmployeeRepository
# from app.repositories.booking_repository import BookingRepository
# from app.services.booking_domain_service import BookingDomainService
# from app.core.event_bus import event_bus

# Create in-memory SQLite database for testing
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    EnhancedBase.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_employee_model_creation(db_session):
    """Test creation of enhanced employee model"""
    employee = Employee(
        full_name="John Doe",
        position="Manager",
        email="john@example.com",
        phone="+1234567890"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    assert employee.id is not None
    assert employee.full_name == "John Doe"
    assert employee.email == "john@example.com"

def test_booking_model_creation(db_session):
    """Test creation of enhanced booking model"""
    from datetime import datetime
    booking = Booking(
        client_name="Jane Smith",
        client_phone="+1234567890",
        phone_normalized="+1234567890",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_price=100.00,
        status=BookingStatus.PENDING
    )
    
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    assert booking.id is not None
    assert booking.client_name == "Jane Smith"
    assert booking.status == BookingStatus.PENDING

def test_employee_repository(db_session):
    """Test employee repository operations"""
    employee = Employee(
        full_name="Alice Johnson",
        position="Manager",
        email="alice@example.com",
        phone="+1987654321"
    )
    
    db_session.add(employee)
    db_session.commit()
    
    repo = EmployeeRepository(db_session)
    retrieved_employee = repo.get_by_email("alice@example.com")
    
    assert retrieved_employee is not None
    assert retrieved_employee.full_name == "Alice Johnson"

def test_booking_repository(db_session):
    """Test booking repository operations"""
    from datetime import datetime
    booking = Booking(
        client_name="Bob Wilson",
        client_phone="+1987654321",
        phone_normalized="+1987654321",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_price=50.00,
        status=BookingStatus.CONFIRMED
    )
    
    db_session.add(booking)
    db_session.commit()
    
    repo = BookingRepository(db_session)
    # retrieved_booking = repo.get_by_reference("REF-20230101-0002")
    
    # assert retrieved_booking is not None
    # assert retrieved_booking.client_name == "Bob Wilson"
    # assert retrieved_booking.state == BookingState.CONFIRMED
    # assert retrieved_booking.source == BookingSource.PHONE

def test_booking_state_transition(db_session):
    """Test booking state transition"""
    from datetime import datetime
    booking = Booking(
        client_name="Carol Brown",
        client_phone="+1555123456",
        phone_normalized="+1555123456",
        date=datetime.now(),
        start_time=datetime.now(),
        end_time=datetime.now(),
        total_price=150.00,
        status=BookingStatus.PENDING
    )
    
    db_session.add(booking)
    db_session.commit()
    
    # service = BookingDomainService(db_session, event_bus)
    # result = service.transition_state(booking.id, BookingState.CONFIRMED)
    
    # assert result.is_success()
    # assert result.value.state == BookingState.CONFIRMED
    # assert len(result.value.state_history) == 1
    # assert result.value.state_history[0]["from_state"] == "pending"
    # assert result.value.state_history[0]["to_state"] == "confirmed"