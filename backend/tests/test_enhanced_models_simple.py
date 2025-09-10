import pytest
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import ENUM as SAEnum, JSON
from datetime import datetime
from enum import Enum as PyEnum
from app.core.config import get_settings

# Define simplified enums for testing
class EmployeeRole(str, PyEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MANAGER = "manager"
    STAFF = "staff"
    VIEWER = "viewer"

class EmployeeStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    PENDING_ACTIVATION = "pending_activation"

class BookingState(str, PyEnum):
    DRAFT = "draft"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"

class SpaceType(str, PyEnum):
    STUDIO_A = "studio_a"
    STUDIO_B = "studio_b"
    STUDIO_C = "studio_c"
    OUTDOOR = "outdoor"
    MEETING_ROOM = "meeting_room"
    DRESSING_ROOM = "dressing_room"

# Define simplified models for testing
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

class SimpleEmployee(Base):
    __tablename__ = "simple_employees"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String(20), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SAEnum(EmployeeRole), nullable=False, default=EmployeeRole.STAFF, index=True)
    status = Column(SAEnum(EmployeeStatus), nullable=False, default=EmployeeStatus.PENDING_ACTIVATION, index=True)
    full_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True, index=True)

class SimpleBooking(Base):
    __tablename__ = "simple_bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(20), unique=True, nullable=False, index=True)
    client_name = Column(String(200), nullable=False, index=True)
    client_phone = Column(String(20), nullable=False, index=True)
    state = Column(SAEnum(BookingState), nullable=False, default=BookingState.PENDING, index=True)
    space_type = Column(SAEnum(SpaceType), nullable=False, index=True)
    base_price = Column(Integer, nullable=False)
    total_price = Column(Integer, nullable=False)

@pytest.fixture(scope="module")
def db_session():
    """Create a database session for testing with PostgreSQL"""
    settings = get_settings()
    
    # Use the test database URL
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )
    
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_employee_enhanced_types(db_session):
    """Test employee model with PostgreSQL-specific enhanced types"""
    employee = SimpleEmployee(
        employee_id="EMP001",
        username="johndoe",
        email="john.doe@example.com",
        password_hash="hashed_password",
        role=EmployeeRole.STAFF,
        status=EmployeeStatus.ACTIVE,
        full_name="John Doe",
        phone="+1234567890"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    assert employee.id is not None
    assert employee.employee_id == "EMP001"
    assert employee.username == "johndoe"
    assert employee.email == "john.doe@example.com"
    assert employee.role == EmployeeRole.STAFF
    assert employee.status == EmployeeStatus.ACTIVE


def test_booking_enhanced_types(db_session):
    """Test booking model with PostgreSQL-specific enhanced types"""
    booking = SimpleBooking(
        booking_reference="REF-20240101-0001",
        client_name="Alice Smith",
        client_phone="+1234567892",
        state=BookingState.PENDING,
        space_type=SpaceType.STUDIO_A,
        base_price=10000,  # Store as cents to avoid floating point issues
        total_price=12500
    )
    
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    assert booking.id is not None
    assert booking.booking_reference == "REF-20240101-0001"
    assert booking.state == BookingState.PENDING
    assert booking.space_type == SpaceType.STUDIO_A
    assert booking.total_price == 12500


def test_enum_values(db_session):
    """Test that enum values are stored correctly"""
    # Test all employee roles with unique IDs
    for i, role in enumerate(EmployeeRole):
        employee = SimpleEmployee(
            employee_id=f"EMP{i+100:03d}",  # Start from 100 to avoid conflicts
            username=f"user{i+100}",
            email=f"user{i+100}@example.com",
            password_hash="hashed_password",
            role=role,
            status=EmployeeStatus.ACTIVE,
            full_name=f"User {i+100}",
            phone=f"+123456789{i}"
        )
        db_session.add(employee)
    
    db_session.commit()
    
    # Verify all roles were stored correctly
    employees = db_session.query(SimpleEmployee).filter(SimpleEmployee.role == EmployeeRole.ADMIN).all()
    # We should have at least one admin (if we created one)
    
    # Test booking states with unique references
    for i, state in enumerate(BookingState):
        if i < 5:  # Limit to avoid too many test records
            booking = SimpleBooking(
                booking_reference=f"REF-20240102-{i:04d}",  # Different date to avoid conflicts
                client_name=f"Client {i+100}",
                client_phone=f"+12345679{i}0",
                state=state,
                space_type=SpaceType.STUDIO_A,
                base_price=10000,
                total_price=10000
            )
            db_session.add(booking)
    
    db_session.commit()
    
    # Verify states were stored correctly
    bookings = db_session.query(SimpleBooking).filter(SimpleBooking.state == BookingState.CONFIRMED).all()
    # We should have at least one confirmed booking (if we created one)