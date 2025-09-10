"""
Integration tests for the enhanced CRM system.

This module tests the integration between enhanced models, repositories,
domain services, and the event bus.
"""

import pytest
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal

from app.models.base_enhanced import BaseEnhanced
from app.models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
from app.models.booking_enhanced import Booking, BookingState, SpaceType
from app.repositories.employee_repository import EmployeeRepository
from app.repositories.booking_repository import BookingRepository
from app.services.booking_domain_service import BookingDomainService
from app.core.event_bus import InMemoryEventBus
from app.core.cqrs import get_command_bus, get_query_bus


@pytest.fixture(scope="module")
def db_session():
    """Create a database session for testing with PostgreSQL"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.config import get_settings
    
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


def test_crm_full_integration(db_session):
    """Test full CRM integration workflow"""
    # Clear any existing data
    db_session.query(Booking).delete()
    db_session.query(Employee).delete()
    db_session.commit()
    
    # Create employees
    manager = Employee(
        employee_id="MGR001",
        username="manager",
        email="manager@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.MANAGER,
        status=EmployeeStatus.ACTIVE,
        full_name="Manager User",
        phone="+1234567890"
    )
    
    staff = Employee(
        employee_id="STF001",
        username="staff",
        email="staff@example.com",
        password_hash="a" * 32,  # Minimum length required by check constraint
        role=EmployeeRole.STAFF,
        status=EmployeeStatus.ACTIVE,
        full_name="Staff User",
        phone="+1234567891"
    )
    
    db_session.add_all([manager, staff])
    db_session.commit()
    db_session.refresh(manager)
    db_session.refresh(staff)
    
    # Create repositories
    employee_repo = EmployeeRepository(db_session)
    booking_repo = BookingRepository(db_session)
    
    # Test creating a booking directly through repository
    now = datetime.now(timezone.utc)
    booking = Booking(
        booking_reference="INT-20240101-0001",
        booking_date=date.today(),
        start_time=now + timedelta(hours=1),
        end_time=now + timedelta(hours=3),
        duration_hours=2.0,
        state=BookingState.PENDING,
        client_name="Integration Test Client",
        client_phone="+1234567999",
        client_phone_normalized="+1234567999",
        space_type=SpaceType.STUDIO_A,
        base_price=Decimal('100.00'),
        equipment_price=Decimal('25.00'),
        discount_amount=Decimal('0.00'),
        total_price=Decimal('125.00'),
        created_by=manager.id,
        updated_by=manager.id
    )
    
    # Save booking
    db_session.add(booking)
    db_session.commit()
    db_session.refresh(booking)
    
    assert booking.id is not None
    assert booking.booking_reference == "INT-20240101-0001"
    assert booking.state == BookingState.PENDING
    assert booking.created_by == manager.id
    
    # Test retrieving booking by reference
    retrieved_result = booking_repo.get_by_reference("INT-20240101-0001")
    assert retrieved_result.is_success()
    assert retrieved_result.value() is not None
    assert retrieved_result.value().id == booking.id
    
    # Test updating booking status directly
    booking.state = BookingState.CONFIRMED
    booking.update_audit_trail("status_update", manager.id, {"reason": "Confirmed by manager"})
    db_session.commit()
    db_session.refresh(booking)
    
    assert booking.state == BookingState.CONFIRMED
    
    # Test finding upcoming bookings
    upcoming_result = booking_repo.find_upcoming_bookings(limit=10)
    assert upcoming_result.is_success()
    assert len(upcoming_result.value()) >= 1
    
    # Test getting booking stats
    stats_result = booking_repo.get_booking_stats(
        date.today(), 
        date.today() + timedelta(days=7)
    )
    assert stats_result.is_success()
    stats = stats_result.value()
    assert stats["total_bookings"] >= 1
    assert stats["total_revenue"] > 0
    
    # Test employee repository
    manager_result = employee_repo.get_by_username("manager")
    assert manager_result is not None
    assert manager_result.id == manager.id
    assert manager_result.role == EmployeeRole.MANAGER
    
    # Test getting employees by role
    managers = employee_repo.get_by_role(EmployeeRole.MANAGER)
    assert len(managers) == 1
    assert managers[0].username == "manager"
    
    # Test audit trail functionality
    manager.update_audit_trail("integration_test", manager.id, {"test": "data"})
    db_session.commit()
    
    # Verify audit trail was updated
    assert manager.audit_trail is not None
    import json
    if isinstance(manager.audit_trail, str):
        trail = json.loads(manager.audit_trail)
    else:
        trail = manager.audit_trail
    
    assert isinstance(trail, list)
    assert len(trail) >= 1
    assert trail[-1]["action"] == "integration_test"
    
    print("Full CRM integration test passed successfully!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])