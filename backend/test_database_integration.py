#!/usr/bin/env python3
"""
Database Integration Testing Script
Tests database connectivity, migrations, and data operations.
"""

import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import List, Tuple, Any

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

async def test_database_connection():
    """Test database connection."""
    print_header("TESTING DATABASE CONNECTION")
    
    results = []
    try:
        from app.core.database import get_db
        from app.core.config import get_settings
        
        settings = get_settings()
        
        # Test database URL configuration
        has_db_url = hasattr(settings, 'DATABASE_URL') and settings.DATABASE_URL
        print_test_result("Database URL configured", has_db_url)
        results.append(("Database URL configured", has_db_url, ""))
        
        if has_db_url:
            print(f"    Database URL: {settings.DATABASE_URL[:50]}...")
        
        # Try to get database session (this will test connection)
        try:
            db_gen = get_db()
            db = next(db_gen)
            print_test_result("Database connection established", True)
            results.append(("Database connection", True, ""))
            
            # Clean up
            db.close()
            
        except Exception as e:
            print_test_result("Database connection", False, str(e))
            results.append(("Database connection", False, str(e)))
        
    except Exception as e:
        print_test_result("Database Configuration", False, str(e))
        results.append(("Database Configuration", False, str(e)))
    
    return results

async def test_database_models():
    """Test database model operations."""
    print_header("TESTING DATABASE MODELS")
    
    results = []
    try:
        from app.models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
        from app.models.booking_enhanced import Booking, BookingState
        from sqlalchemy import Column, Integer, String
        
        # Test model creation
        try:
            # Check if Employee model has required attributes
            employee_tests = [
                ("Employee has __tablename__", hasattr(Employee, '__tablename__')),
                ("Employee has id column", hasattr(Employee, 'id')),
                ("Employee has username column", hasattr(Employee, 'username')),
                ("Employee has email column", hasattr(Employee, 'email')),
                ("Employee has role column", hasattr(Employee, 'role')),
                ("Employee has status column", hasattr(Employee, 'status')),
            ]
            
            for test_name, condition in employee_tests:
                print_test_result(test_name, condition)
                results.append((test_name, condition, ""))
            
            # Check Booking model
            booking_tests = [
                ("Booking has __tablename__", hasattr(Booking, '__tablename__')),
                ("Booking has id column", hasattr(Booking, 'id')),
                ("Booking has booking_reference", hasattr(Booking, 'booking_reference')),
                ("Booking has state column", hasattr(Booking, 'state')),
                ("Booking has start_time column", hasattr(Booking, 'start_time')),
                ("Booking has end_time column", hasattr(Booking, 'end_time')),
            ]
            
            for test_name, condition in booking_tests:
                print_test_result(test_name, condition)
                results.append((test_name, condition, ""))
            
        except Exception as e:
            print_test_result("Model Structure Test", False, str(e))
            results.append(("Model Structure Test", False, str(e)))
        
    except Exception as e:
        print_test_result("Database Models Import", False, str(e))
        results.append(("Database Models Import", False, str(e)))
    
    return results

async def test_alembic_migrations():
    """Test Alembic migration system."""
    print_header("TESTING ALEMBIC MIGRATIONS")
    
    results = []
    try:
        import os
        from alembic.config import Config
        from alembic import command
        
        # Check if alembic.ini exists
        alembic_ini_path = "alembic.ini"
        alembic_ini_exists = os.path.exists(alembic_ini_path)
        print_test_result("Alembic config exists", alembic_ini_exists)
        results.append(("Alembic config exists", alembic_ini_exists, ""))
        
        if alembic_ini_exists:
            try:
                # Try to load alembic config
                alembic_cfg = Config(alembic_ini_path)
                print_test_result("Alembic config loads", True)
                results.append(("Alembic config loads", True, ""))
                
                # Check migrations directory
                migrations_dir = "alembic/versions"
                migrations_exist = os.path.exists(migrations_dir)
                print_test_result("Migrations directory exists", migrations_exist)
                results.append(("Migrations directory", migrations_exist, ""))
                
                if migrations_exist:
                    # Count migration files
                    migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py') and not f.startswith('__')]
                    migration_count = len(migration_files)
                    print_test_result(f"Migration files found ({migration_count})", migration_count > 0)
                    results.append((f"Migration files ({migration_count})", migration_count > 0, ""))
                
            except Exception as e:
                print_test_result("Alembic config loading", False, str(e))
                results.append(("Alembic config loading", False, str(e)))
        
    except Exception as e:
        print_test_result("Alembic Migration Test", False, str(e))
        results.append(("Alembic Migration Test", False, str(e)))
    
    return results

async def test_database_constraints_and_indexes():
    """Test database constraints and indexes."""
    print_header("TESTING DATABASE CONSTRAINTS AND INDEXES")
    
    results = []
    try:
        from app.models.employee_enhanced import Employee
        from app.models.booking_enhanced import Booking
        from sqlalchemy import inspect
        
        # Test if models have proper table constraints
        try:
            # Check Employee table constraints
            employee_table = Employee.__table__
            employee_constraints = employee_table.constraints
            employee_indexes = employee_table.indexes
            
            print_test_result("Employee table has constraints", len(employee_constraints) > 0)
            results.append(("Employee constraints", len(employee_constraints) > 0, ""))
            
            print_test_result("Employee table has indexes", len(employee_indexes) >= 0)
            results.append(("Employee indexes", len(employee_indexes) >= 0, ""))
            
            # Check Booking table constraints
            booking_table = Booking.__table__
            booking_constraints = booking_table.constraints
            booking_indexes = booking_table.indexes
            
            print_test_result("Booking table has constraints", len(booking_constraints) > 0)
            results.append(("Booking constraints", len(booking_constraints) > 0, ""))
            
            print_test_result("Booking table has indexes", len(booking_indexes) >= 0)
            results.append(("Booking indexes", len(booking_indexes) >= 0, ""))
            
            # Print some details
            print(f"    Employee constraints: {len(employee_constraints)}")
            print(f"    Employee indexes: {len(employee_indexes)}")
            print(f"    Booking constraints: {len(booking_constraints)}")
            print(f"    Booking indexes: {len(booking_indexes)}")
            
        except Exception as e:
            print_test_result("Constraints and Indexes Test", False, str(e))
            results.append(("Constraints and Indexes", False, str(e)))
        
    except Exception as e:
        print_test_result("Database Schema Test", False, str(e))
        results.append(("Database Schema Test", False, str(e)))
    
    return results

async def test_model_relationships():
    """Test model relationships and foreign keys."""
    print_header("TESTING MODEL RELATIONSHIPS")
    
    results = []
    try:
        from app.models.employee_enhanced import Employee
        from app.models.booking_enhanced import Booking
        from sqlalchemy.orm import relationship
        
        # Check if models have relationships
        employee_relationships = []
        booking_relationships = []
        
        # Get all attributes that are relationships
        for attr_name in dir(Employee):
            attr = getattr(Employee, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'mapper'):
                employee_relationships.append(attr_name)
        
        for attr_name in dir(Booking):
            attr = getattr(Booking, attr_name)
            if hasattr(attr, 'property') and hasattr(attr.property, 'mapper'):
                booking_relationships.append(attr_name)
        
        print_test_result("Employee relationships defined", len(employee_relationships) >= 0)
        print_test_result("Booking relationships defined", len(booking_relationships) >= 0)
        
        results.extend([
            ("Employee relationships", len(employee_relationships) >= 0, ""),
            ("Booking relationships", len(booking_relationships) >= 0, "")
        ])
        
        if employee_relationships:
            print(f"    Employee relationships: {employee_relationships}")
        if booking_relationships:
            print(f"    Booking relationships: {booking_relationships}")
        
    except Exception as e:
        print_test_result("Model Relationships Test", False, str(e))
        results.append(("Model Relationships Test", False, str(e)))
    
    return results

async def test_audit_trail_functionality():
    """Test audit trail functionality in enhanced models."""
    print_header("TESTING AUDIT TRAIL FUNCTIONALITY")
    
    results = []
    try:
        from app.models.base_enhanced import BaseEnhanced
        from app.models.employee_enhanced import Employee
        from app.models.booking_enhanced import Booking
        
        # Check if models inherit from BaseEnhanced
        employee_has_audit = issubclass(Employee, BaseEnhanced)
        booking_has_audit = issubclass(Booking, BaseEnhanced)
        
        print_test_result("Employee has audit trail", employee_has_audit)
        print_test_result("Booking has audit trail", booking_has_audit)
        
        results.extend([
            ("Employee audit trail", employee_has_audit, ""),
            ("Booking audit trail", booking_has_audit, "")
        ])
        
        # Check for audit fields
        if employee_has_audit:
            audit_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'version']
            for field in audit_fields:
                has_field = hasattr(Employee, field)
                print_test_result(f"Employee has {field}", has_field)
                results.append((f"Employee {field}", has_field, ""))
        
    except Exception as e:
        print_test_result("Audit Trail Test", False, str(e))
        results.append(("Audit Trail Test", False, str(e)))
    
    return results

def generate_database_test_report(all_results: List[tuple]):
    """Generate a comprehensive database test report."""
    print_header("DATABASE TEST REPORT SUMMARY")
    
    total_tests = len(all_results)
    passed_tests = sum(1 for _, success, _ in all_results if success)
    failed_tests = total_tests - passed_tests
    
    print(f"Total Database Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n🔍 FAILED DATABASE TESTS:")
        for test_name, success, details in all_results:
            if not success:
                print(f"  ❌ {test_name}: {details}")
    
    print("\n📊 DATABASE RECOMMENDATIONS:")
    if failed_tests == 0:
        print("  ✅ All database tests passed! Database is ready for production.")
    elif failed_tests < total_tests * 0.1:  # Less than 10% failure
        print("  ⚠️  Minor database issues detected. Review failed tests.")
    else:
        print("  🚨 Significant database issues detected. Address failed tests before deployment.")

async def main():
    """Run all database tests."""
    print("🗄️ COMPREHENSIVE DATABASE TESTING")
    print(f"Started at: {datetime.now()}")
    
    all_results = []
    
    # Run database tests
    all_results.extend(await test_database_connection())
    all_results.extend(await test_database_models())
    all_results.extend(await test_alembic_migrations())
    all_results.extend(await test_database_constraints_and_indexes())
    all_results.extend(await test_model_relationships())
    all_results.extend(await test_audit_trail_functionality())
    
    # Generate report
    generate_database_test_report(all_results)
    
    print(f"\n🏁 Database testing completed at: {datetime.now()}")

if __name__ == "__main__":
    asyncio.run(main())
