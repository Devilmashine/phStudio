import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.models.base_enhanced import BaseEnhanced
from app.models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
from app.models.booking_enhanced import Booking, BookingState, SpaceType
from app.core.config import get_settings

# Test with PostgreSQL database
@pytest.fixture(scope="module")
def db_session():
    """Create a database session for testing with PostgreSQL"""
    settings = get_settings()
    
    # Use the test database URL
    engine = create_engine(
        settings.TEST_DATABASE_URL,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True
    )
    
    # Create tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    BaseEnhanced.metadata.drop_all(bind=engine)
    BaseEnhanced.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)
    BaseEnhanced.metadata.drop_all(bind=engine)


def test_employee_model_with_postgresql_types(db_session):
    """Test creation of employee model with PostgreSQL-specific types"""
    employee = Employee(
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


def test_booking_model_with_postgresql_types(db_session):
    """Test creation of booking model with PostgreSQL-specific types"""
    from datetime import datetime, date, timezone
    
    # Create employee first (foreign key constraint)
    employee = Employee(
        employee_id="EMP002",
        username="janedoe",
        email="jane.doe@example.com",
        password_hash="hashed_password",
        role=EmployeeRole.MANAGER,
        status=EmployeeStatus.ACTIVE,
        full_name="Jane Doe",
        phone="+1234567891"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    # Create booking
    booking = Booking(
        booking_reference="REF-20240101-0001",
        booking_date=date.today(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        duration_hours=2.0,
        state=BookingState.PENDING,
        client_name="Alice Smith",
        client_phone="+1234567892",
        client_phone_normalized="+1234567892",
        space_type=SpaceType.STUDIO_A,
        base_price=100.00,
        equipment_price=25.00,
        discount_amount=0.00,
        total_price=125.00,
        created_by=employee.id,
        updated_by=employee.id
    )
    
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    assert booking.id is not None
    assert booking.booking_reference == "REF-20240101-0001"
    assert booking.state == BookingState.PENDING
    assert booking.space_type == SpaceType.STUDIO_A
    assert booking.total_price == 125.00


def test_employee_repository_with_postgresql(db_session):
    """Test employee repository operations with PostgreSQL"""
    from app.repositories.employee_repository import EmployeeRepository
    
    # Create employee
    employee = Employee(
        employee_id="EMP003",
        username="bobwilson",
        email="bob.wilson@example.com",
        password_hash="hashed_password",
        role=EmployeeRole.ADMIN,
        status=EmployeeStatus.ACTIVE,
        full_name="Bob Wilson",
        phone="+1234567893"
    )
    
    db_session.add(employee)
    db_session.commit()
    
    # Test repository
    repo = EmployeeRepository(db_session)
    retrieved_employee = repo.get_by_email("bob.wilson@example.com")
    
    assert retrieved_employee is not None
    assert retrieved_employee.full_name == "Bob Wilson"
    assert retrieved_employee.role == EmployeeRole.ADMIN


def test_booking_repository_with_postgresql(db_session):
    """Test booking repository operations with PostgreSQL"""
    from app.repositories.booking_repository import BookingRepository
    from datetime import datetime, date, timezone
    
    # Create employee
    employee = Employee(
        employee_id="EMP004",
        username="sallyjones",
        email="sally.jones@example.com",
        password_hash="hashed_password",
        role=EmployeeRole.STAFF,
        status=EmployeeStatus.ACTIVE,
        full_name="Sally Jones",
        phone="+1234567894"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    # Create booking
    booking = Booking(
        booking_reference="REF-20240101-0002",
        booking_date=date.today(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc),
        duration_hours=1.5,
        state=BookingState.CONFIRMED,
        client_name="Charlie Brown",
        client_phone="+1234567895",
        client_phone_normalized="+1234567895",
        space_type=SpaceType.STUDIO_B,
        base_price=75.00,
        equipment_price=15.00,
        discount_amount=5.00,
        total_price=85.00,
        created_by=employee.id,
        updated_by=employee.id
    )
    
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    # Test repository
    repo = BookingRepository(db_session)
    retrieved_booking = repo.get_by_reference("REF-20240101-0002")
    
    assert retrieved_booking.is_success()
    assert retrieved_booking.value is not None
    assert retrieved_booking.value.client_name == "Charlie Brown"
    assert retrieved_booking.value.total_price == 85.00