#!/usr/bin/env python3
"""
Comprehensive Testing Script for Photo Studio CRM Backend
This script tests all major components and identifies potential issues.
"""

import asyncio
import os
import sys
import traceback
from datetime import datetime
from typing import Dict, List, Any

# Add app to path
sys.path.append('.')

def print_header(title: str):
    """Print a formatted header for test sections."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test_result(test_name: str, success: bool, details: str = ""):
    """Print formatted test results."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

def test_imports():
    """Test all critical imports."""
    print_header("TESTING IMPORTS")
    
    test_cases = [
        ("FastAPI App", "from app.main import app"),
        ("Database Config", "from app.core.database import get_db"),
        ("Settings", "from app.core.config import get_settings"),
        ("Security", "from app.core.security import verify_password"),
        ("Models", "from app.models.employee import Employee"),
        ("Enhanced Models", "from app.models.employee_enhanced import Employee as EnhancedEmployee"),
        ("Booking Models", "from app.models.booking_enhanced import Booking"),
        ("Event Bus", "from app.core.event_bus import EventBus"),
        ("CQRS", "from app.core.cqrs import CommandBus, QueryBus"),
        ("Cache", "from app.core.cache import CacheService"),
    ]
    
    results = []
    for test_name, import_statement in test_cases:
        try:
            exec(import_statement)
            print_test_result(test_name, True)
            results.append((test_name, True, ""))
        except ImportError as e:
            print_test_result(test_name, False, f"Import error: {e}")
            results.append((test_name, False, str(e)))
        except Exception as e:
            print_test_result(test_name, False, f"Error: {e}")
            results.append((test_name, False, str(e)))
    
    return results

def test_configuration():
    """Test configuration and environment variables."""
    print_header("TESTING CONFIGURATION")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        test_cases = [
            ("Database URL", hasattr(settings, 'DATABASE_URL')),
            ("Secret Key", hasattr(settings, 'SECRET_KEY')),
            ("Redis URL", hasattr(settings, 'REDIS_URL')),
            ("Environment", hasattr(settings, 'ENV')),
            ("CORS Origins", hasattr(settings, 'CORS_ORIGINS')),
            ("Telegram Config", settings.validate_telegram_config() if hasattr(settings, 'validate_telegram_config') else True),
        ]
        
        results = []
        for test_name, condition in test_cases:
            print_test_result(test_name, condition)
            results.append((test_name, condition, ""))
        
        return results
        
    except Exception as e:
        print_test_result("Configuration Test", False, str(e))
        return [("Configuration Test", False, str(e))]

def test_database_models():
    """Test database model definitions."""
    print_header("TESTING DATABASE MODELS")
    
    results = []
    try:
        from app.models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
        from app.models.booking_enhanced import Booking, BookingState
        from app.models.base_enhanced import BaseEnhanced
        
        # Test Employee model
        test_cases = [
            ("Employee Model Import", True),
            ("Employee Roles Enum", len(EmployeeRole) > 0),
            ("Employee Status Enum", len(EmployeeStatus) > 0),
            ("Employee Table Name", hasattr(Employee, '__tablename__')),
            ("Employee Enhanced Base", issubclass(Employee, BaseEnhanced)),
        ]
        
        for test_name, condition in test_cases:
            print_test_result(test_name, condition)
            results.append((test_name, condition, ""))
        
        # Test Booking model
        booking_tests = [
            ("Booking Model Import", True),
            ("Booking States Enum", len(BookingState) > 0),
            ("Booking Table Name", hasattr(Booking, '__tablename__')),
            ("Booking Enhanced Base", issubclass(Booking, BaseEnhanced)),
        ]
        
        for test_name, condition in booking_tests:
            print_test_result(test_name, condition)
            results.append((test_name, condition, ""))
            
    except Exception as e:
        print_test_result("Database Models Test", False, str(e))
        results.append(("Database Models Test", False, str(e)))
    
    return results

def test_api_routes():
    """Test API route definitions."""
    print_header("TESTING API ROUTES")
    
    results = []
    try:
        from app.main import app
        from fastapi.routing import APIRoute
        
        # Get all routes
        routes = []
        for route in app.routes:
            if isinstance(route, APIRoute):
                routes.append(f"{route.methods} {route.path}")
        
        # Check for expected routes
        expected_routes = [
            "auth",
            "bookings", 
            "employees",
            "kanban",
            "calendar",
            "health"
        ]
        
        route_str = " ".join(routes)
        for expected in expected_routes:
            found = expected in route_str
            print_test_result(f"Route '{expected}' exists", found)
            results.append((f"Route '{expected}'", found, ""))
        
        print(f"\nTotal routes found: {len(routes)}")
        
    except Exception as e:
        print_test_result("API Routes Test", False, str(e))
        results.append(("API Routes Test", False, str(e)))
    
    return results

async def test_async_components():
    """Test async components like database connections."""
    print_header("TESTING ASYNC COMPONENTS")
    
    results = []
    try:
        # Test event bus - use concrete implementation
        from app.core.event_bus import InMemoryEventBus, EventType, DomainEvent, EventHandler, EventMetadata
        from typing import Optional
        
        # Create a simple test event
        class TestEvent(DomainEvent):
            def __init__(self, data: dict):
                super().__init__()
                self.data = data
            
            @property
            def event_type(self) -> EventType:
                return EventType.AUDIT_LOG_CREATED  # Use existing event type
            
            @property
            def aggregate_id(self) -> str:
                return "test-aggregate"
        
        # Create a simple test handler
        class TestHandler(EventHandler):
            def __init__(self):
                self.handled_events = []
            
            async def handle(self, event: DomainEvent) -> None:
                self.handled_events.append(event)
        
        # Test the event bus
        event_bus = InMemoryEventBus()
        test_handler = TestHandler()
        
        # Subscribe and publish
        await event_bus.subscribe(EventType.AUDIT_LOG_CREATED, test_handler)
        test_event = TestEvent({"test": True})
        await event_bus.publish(test_event)
        
        # Check if event was handled
        test_event_fired = len(test_handler.handled_events) > 0
        
        print_test_result("Event Bus Publish/Subscribe", test_event_fired)
        results.append(("Event Bus", test_event_fired, ""))
        
        # Test cache service if available
        try:
            from app.core.cache import CacheService
            # This might fail if Redis is not available, which is expected
            print_test_result("Cache Service Import", True)
            results.append(("Cache Service Import", True, ""))
        except Exception as e:
            print_test_result("Cache Service", False, f"Redis may not be available: {e}")
            results.append(("Cache Service", False, str(e)))
        
    except Exception as e:
        print_test_result("Async Components Test", False, str(e))
        results.append(("Async Components Test", False, str(e)))
    
    return results

def test_security_components():
    """Test security-related components."""
    print_header("TESTING SECURITY COMPONENTS")
    
    results = []
    try:
        from app.core.security import verify_password, get_password_hash, create_access_token
        
        # Test password hashing
        test_password = "test_password_123"
        hashed = get_password_hash(test_password)
        verified = verify_password(test_password, hashed)
        
        print_test_result("Password Hashing", isinstance(hashed, str) and len(hashed) > 20)
        print_test_result("Password Verification", verified)
        results.extend([
            ("Password Hashing", isinstance(hashed, str) and len(hashed) > 20, ""),
            ("Password Verification", verified, "")
        ])
        
        # Test token creation
        try:
            token = create_access_token({"sub": "test_user"})
            print_test_result("JWT Token Creation", isinstance(token, str) and len(token) > 20)
            results.append(("JWT Token Creation", isinstance(token, str) and len(token) > 20, ""))
        except Exception as e:
            print_test_result("JWT Token Creation", False, str(e))
            results.append(("JWT Token Creation", False, str(e)))
        
    except Exception as e:
        print_test_result("Security Components Test", False, str(e))
        results.append(("Security Components Test", False, str(e)))
    
    return results

def test_pydantic_models():
    """Test Pydantic model definitions for API schemas."""
    print_header("TESTING PYDANTIC MODELS")
    
    results = []
    try:
        # Try to find and test various schema models
        schema_modules = [
            "app.api.routes.auth",
            "app.api.routes.booking",
            "app.api.routes.employees",
        ]
        
        for module_name in schema_modules:
            try:
                __import__(module_name)
                print_test_result(f"Schema module {module_name}", True)
                results.append((f"Schema {module_name}", True, ""))
            except ImportError as e:
                print_test_result(f"Schema module {module_name}", False, str(e))
                results.append((f"Schema {module_name}", False, str(e)))
        
    except Exception as e:
        print_test_result("Pydantic Models Test", False, str(e))
        results.append(("Pydantic Models Test", False, str(e)))
    
    return results

def generate_test_report(all_results: List[tuple]):
    """Generate a comprehensive test report."""
    print_header("TEST REPORT SUMMARY")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success, _ in all_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n🔍 FAILED TESTS:")
        for test_name, success, details in all_results:
            if not success:
                print(f"  ❌ {test_name}: {details}")
    
    print("\n📊 RECOMMENDATIONS:")
    if failed_tests == 0:
        print("  ✅ All tests passed! System is ready for production.")
    elif failed_tests < total_tests * 0.1:  # Less than 10% failure
        print("  ⚠️  Minor issues detected. Review failed tests.")
    else:
        print("  🚨 Significant issues detected. Address failed tests before deployment.")

async def main():
    """Run all tests."""
    print("🧪 COMPREHENSIVE BACKEND TESTING")
    print(f"Started at: {datetime.now()}")
    
    all_results = []
    
    # Run synchronous tests
    all_results.extend(test_imports())
    all_results.extend(test_configuration())
    all_results.extend(test_database_models())
    all_results.extend(test_api_routes())
    all_results.extend(test_security_components())
    all_results.extend(test_pydantic_models())
    
    # Run async tests
    async_results = await test_async_components()
    all_results.extend(async_results)
    
    # Generate report
    generate_test_report(all_results)
    
    print(f"\n🏁 Testing completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())
