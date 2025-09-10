import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from app.models.base_enhanced import BaseEnhanced
from app.models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
from app.models.booking_enhanced import Booking, BookingState, SpaceType, PaymentStatus
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.booking_repository import BookingRepository
from app.core.config import get_settings

# Test with PostgreSQL database
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
    BaseEnhanced.metadata.drop_all(bind=engine)
    BaseEnhanced.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    BaseEnhanced.metadata.drop_all(bind=engine)


def test_employee_enhanced_model_creation(db_session):
    """Test creation of enhanced employee model with all fields"""
    # Clear any existing employees
    db_session.query(Employee).delete()
    db_session.commit()
    
    employee = Employee(
        employee_id="EMP001",
        username="johndoe",
        email="john.doe@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.MANAGER,
        status=EmployeeStatus.ACTIVE,
        full_name="John Doe",
        phone="+1234567890",
        department="Photography",
        position="Senior Photographer"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    assert employee.id is not None
    assert employee.employee_id == "EMP001"
    assert employee.username == "johndoe"
    assert employee.email == "john.doe@example.com"
    assert employee.role == EmployeeRole.MANAGER
    assert employee.status == EmployeeStatus.ACTIVE
    assert employee.full_name == "John Doe"
    assert employee.phone == "+1234567890"
    assert employee.department == "Photography"
    assert employee.position == "Senior Photographer"
    assert employee.created_at is not None
    assert employee.updated_at is not None
    assert employee.version == 1
    assert employee.is_deleted is False


def test_employee_enhanced_security_features(db_session):
    """Test employee security features"""
    # Clear any existing employees
    db_session.query(Employee).delete()
    db_session.commit()
    
    employee = Employee(
        employee_id="EMP002",
        username="janedoe",
        email="jane.doe@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.STAFF,
        status=EmployeeStatus.ACTIVE,
        full_name="Jane Doe",
        phone="+1234567891"
    )
    
    # Test MFA features
    employee.mfa_enabled = True
    employee.mfa_secret = "SECRET123"
    
    # Test password security features
    employee.password_changed_at = datetime.now(timezone.utc)
    employee.password_expires_at = datetime.now(timezone.utc) + timedelta(days=90)
    
    # Test account security features
    employee.failed_login_attempts = 0
    employee.last_login = datetime.now(timezone.utc)
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    assert employee.mfa_enabled is True
    assert employee.mfa_secret == "SECRET123"
    assert employee.password_changed_at is not None
    assert employee.password_expires_at is not None
    assert employee.failed_login_attempts == 0
    assert employee.last_login is not None


def test_booking_enhanced_model_creation(db_session):
    """Test creation of enhanced booking model with all fields"""
    # Clear any existing bookings and employees
    db_session.query(Booking).delete()
    db_session.query(Employee).delete()
    db_session.commit()
    
    # Create employee first (foreign key constraint)
    employee = Employee(
        employee_id="EMP003",
        username="bobwilson",
        email="bob.wilson@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.MANAGER,
        status=EmployeeStatus.ACTIVE,
        full_name="Bob Wilson",
        phone="+1234567892"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    # Create booking
    booking = Booking(
        booking_reference="REF-20240101-0001",
        booking_date=date.today(),
        start_time=datetime.now(timezone.utc),
        end_time=datetime.now(timezone.utc) + timedelta(hours=2),
        duration_hours=2.0,
        state=BookingState.PENDING,
        client_name="Alice Smith",
        client_phone="+1234567893",
        client_phone_normalized="+1234567893",
        space_type=SpaceType.STUDIO_A,
        base_price=Decimal('100.00'),
        equipment_price=Decimal('25.00'),
        discount_amount=Decimal('0.00'),
        total_price=Decimal('125.00'),
        created_by=employee.id,
        updated_by=employee.id
    )
    
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    assert booking.id is not None
    assert booking.booking_reference == "REF-20240101-0001"
    assert booking.state == BookingState.PENDING
    assert booking.client_name == "Alice Smith"
    assert booking.client_phone == "+1234567893"
    assert booking.space_type == SpaceType.STUDIO_A
    assert booking.base_price == Decimal('100.00')
    assert booking.equipment_price == Decimal('25.00')
    assert booking.total_price == Decimal('125.00')
    assert booking.created_at is not None
    assert booking.updated_at is not None
    assert booking.version == 1
    assert booking.is_deleted is False


def test_booking_enhanced_state_machine(db_session):
    """Test booking state machine functionality"""
    # Clear any existing bookings and employees
    db_session.query(Booking).delete()
    db_session.query(Employee).delete()
    db_session.commit()
    
    # Create employee first (foreign key constraint)
    employee = Employee(
        employee_id="EMP004",
        username="sallyjones",
        email="sally.jones@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.MANAGER,
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
        end_time=datetime.now(timezone.utc) + timedelta(hours=3),
        duration_hours=3.0,
        state=BookingState.DRAFT,
        client_name="Charlie Brown",
        client_phone="+1234567895",
        client_phone_normalized="+1234567895",
        space_type=SpaceType.STUDIO_B,
        base_price=Decimal('150.00'),
        equipment_price=Decimal('30.00'),
        discount_amount=Decimal('0.00'),
        total_price=Decimal('180.00'),
        created_by=employee.id,
        updated_by=employee.id
    )
    
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    # Test state transition
    success = booking.transition_to(BookingState.PENDING, employee.id, "Ready for review")
    assert success is True
    assert booking.state == BookingState.PENDING
    import json
    state_history = json.loads(booking.state_history)
    assert len(state_history) == 1
    assert state_history[0]["state"] == "pending"
    
    # Test another state transition
    success = booking.transition_to(BookingState.CONFIRMED, employee.id, "Client confirmed")
    assert success is True
    assert booking.state == BookingState.CONFIRMED
    state_history = json.loads(booking.state_history)
    assert len(state_history) == 2
    assert state_history[1]["state"] == "confirmed"


def test_employee_repository_enhanced(db_session):
    """Test employee repository with enhanced features"""
    # Clear any existing employees
    db_session.query(Employee).delete()
    db_session.commit()
    
    # Create employees
    employee1 = Employee(
        employee_id="EMP005",
        username="user1",
        email="user1@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.ADMIN,
        status=EmployeeStatus.ACTIVE,
        full_name="User One",
        phone="+1234567896"
    )
    
    employee2 = Employee(
        employee_id="EMP006",
        username="user2",
        email="user2@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.STAFF,
        status=EmployeeStatus.ACTIVE,
        full_name="User Two",
        phone="+1234567897"
    )
    
    employee3 = Employee(
        employee_id="EMP007",
        username="user3",
        email="user3@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.MANAGER,
        status=EmployeeStatus.INACTIVE,
        full_name="User Three",
        phone="+1234567898"
    )
    
    db_session.add_all([employee1, employee2, employee3])
    db_session.commit()
    
    # Test repository
    repo = EmployeeRepository(db_session)
    
    # Test get by username
    retrieved_employee = repo.get_by_username("user1")
    assert retrieved_employee is not None
    assert retrieved_employee.full_name == "User One"
    assert retrieved_employee.role == EmployeeRole.ADMIN
    
    # Test get by email
    retrieved_employee = repo.get_by_email("user2@example.com")
    assert retrieved_employee is not None
    assert retrieved_employee.username == "user2"
    assert retrieved_employee.role == EmployeeRole.STAFF
    
    # Test get by role
    managers = repo.get_by_role(EmployeeRole.MANAGER)
    assert len(managers) == 1
    assert managers[0].full_name == "User Three"
    
    # Test get active employees
    active_employees = repo.get_active_employees()
    assert len(active_employees) == 2  # Only user1 and user2 are active
    
    # Test get employees by status
    inactive_employees = repo.get_employees_by_status(EmployeeStatus.INACTIVE)
    assert len(inactive_employees) == 1
    assert inactive_employees[0].full_name == "User Three"


def test_booking_repository_enhanced(db_session):
    """Test booking repository with enhanced features"""
    # Clear any existing bookings and employees
    db_session.query(Booking).delete()
    db_session.query(Employee).delete()
    db_session.commit()
    
    # Create employee first (foreign key constraint)
    employee = Employee(
        employee_id="EMP008",
        username="testuser",
        email="test@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.MANAGER,
        status=EmployeeStatus.ACTIVE,
        full_name="Test User",
        phone="+1234567899"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    # Create bookings with different states and future start times
    now = datetime.now(timezone.utc)
    
    booking1 = Booking(
        booking_reference="REF-20240101-0003",
        booking_date=date.today(),
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        duration_hours=2.0,
        state=BookingState.PENDING,
        client_name="Client One",
        client_phone="+1234567001",
        client_phone_normalized="+1234567001",
        space_type=SpaceType.STUDIO_A,
        base_price=Decimal('100.00'),
        equipment_price=Decimal('0.00'),
        discount_amount=Decimal('0.00'),
        total_price=Decimal('100.00'),
        created_by=employee.id,
        updated_by=employee.id
    )
    
    booking2 = Booking(
        booking_reference="REF-20240101-0004",
        booking_date=date.today() + timedelta(days=1),
        start_time=now + timedelta(days=1, hours=2),
        end_time=now + timedelta(days=1, hours=5),
        duration_hours=3.0,
        state=BookingState.CONFIRMED,
        client_name="Client Two",
        client_phone="+1234567002",
        client_phone_normalized="+1234567002",
        space_type=SpaceType.STUDIO_B,
        base_price=Decimal('150.00'),
        equipment_price=Decimal('25.00'),
        discount_amount=Decimal('0.00'),
        total_price=Decimal('175.00'),
        created_by=employee.id,
        updated_by=employee.id
    )
    
    booking3 = Booking(
        booking_reference="REF-20240101-0005",
        booking_date=date.today() + timedelta(days=2),
        start_time=now + timedelta(days=2, hours=3),
        end_time=now + timedelta(days=2, hours=4),
        duration_hours=1.0,
        state=BookingState.COMPLETED,
        client_name="Client Three",
        client_phone="+1234567003",
        client_phone_normalized="+1234567003",
        space_type=SpaceType.STUDIO_C,
        base_price=Decimal('75.00'),
        equipment_price=Decimal('0.00'),
        discount_amount=Decimal('10.00'),
        total_price=Decimal('65.00'),
        created_by=employee.id,
        updated_by=employee.id
    )
    
    db_session.add_all([booking1, booking2, booking3])
    db_session.commit()
    
    # Test repository
    repo = BookingRepository(db_session)
    
    # Test get by reference
    result = repo.get_by_reference("REF-20240101-0003")
    assert result.is_success()
    assert result.value() is not None
    assert result.value().client_name == "Client One"
    assert result.value().state == BookingState.PENDING
    
    # Test find by filters
    result = repo.find_by_filters({"state": BookingState.CONFIRMED})
    assert result.is_success()
    assert len(result.value()) == 1
    assert result.value()[0].client_name == "Client Two"
    
    # Test find upcoming bookings
    result = repo.find_upcoming_bookings(limit=10)
    assert result.is_success()
    # Should find at least the pending and confirmed bookings
    assert len(result.value()) >= 2
    
    # Test get booking stats
    result = repo.get_booking_stats(date.today(), date.today() + timedelta(days=2))
    assert result.is_success()
    stats = result.value()
    assert stats["total_bookings"] >= 3
    assert stats["total_revenue"] > 0
    assert "completion_rate" in stats
    assert "cancellation_rate" in stats


def test_enhanced_model_audit_features(db_session):
    """Test audit features of enhanced models"""
    # Clear any existing employees
    db_session.query(Employee).delete()
    db_session.commit()
    
    # Create employee
    employee = Employee(
        employee_id="EMP009",
        username="audituser",
        email="audit@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.ADMIN,
        status=EmployeeStatus.ACTIVE,
        full_name="Audit User",
        phone="+1234567010"
    )
    
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(employee)
    
    # Test audit trail
    employee.update_audit_trail("test_action", employee.id, {"test": "data"})
    db_session.commit()
    
    assert employee.audit_trail is not None
    # The audit trail should be a list with at least one entry
    if isinstance(employee.audit_trail, str):
        import json
        trail = json.loads(employee.audit_trail)
    else:
        trail = employee.audit_trail
    
    assert isinstance(trail, list)
    assert len(trail) >= 1
    assert trail[-1]["action"] == "test_action"
    assert trail[-1]["user_id"] == employee.id
    
    # Test version increment
    original_version = employee.version
    employee.increment_version()
    db_session.commit()
    
    assert employee.version == original_version + 1
    
    # Test soft delete
    employee.soft_delete(employee.id, "test deletion")
    db_session.commit()
    
    assert employee.is_deleted is True
    assert employee.deleted_at is not None
    assert employee.deleted_by == employee.id
    
    # Test restore
    employee.restore(employee.id)
    db_session.commit()
    
    assert employee.is_deleted is False
    assert employee.deleted_at is None
    assert employee.deleted_by is None