#!/usr/bin/env python3
"""
Script to clear all users and employees and create one user of each type for testing.
This script is designed for testing CRM and administrative functions.
"""

import os
import sys
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timezone
from secrets import token_urlsafe

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_engine, get_session_local
from app.models.user import User, UserRole
from app.models.employee_enhanced import Employee
from app.models.booking import Booking
from app.models.news import News
from app.models.base import Base

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db_session():
    """Get database session"""
    engine = get_engine()
    SessionLocal = get_session_local()
    return SessionLocal()

def clear_all_data(db: Session):
    """Clear all data from the database in the correct order to respect foreign key constraints"""
    print("Clearing all data from the database...")
    
    # Delete in order to respect foreign key constraints
    # 1. News (depends on users)
    news_count = db.query(News).delete()
    print(f"Deleted {news_count} news articles")
    
    # 2. Bookings (depends on users)
    booking_count = db.query(Booking).delete()
    print(f"Deleted {booking_count} bookings")
    
    # 3. Users
    user_count = db.query(User).delete()
    print(f"Deleted {user_count} users")
    
    # 4. Employees
    employee_count = db.query(Employee).delete()
    print(f"Deleted {employee_count} employees")
    
    # Commit changes
    db.commit()
    print("All data cleared successfully")

def create_test_users(db: Session):
    """Create one user of each type for testing"""
    print("Creating test users...")
    
    # Common password for all test users
    test_password = "TestPass123!"
    hashed_password = pwd_context.hash(test_password)
    
    # Create users with different roles
    users_data = [
        {
            "username": "testuser",
            "email": "user@test.com",
            "full_name": "Test User",
            "role": UserRole.user,
            "hashed_password": hashed_password,
            "ical_token": token_urlsafe(32),
            "is_active": "true"
        },
        {
            "username": "testadmin",
            "email": "admin@test.com",
            "full_name": "Test Admin",
            "role": UserRole.admin,
            "hashed_password": hashed_password,
            "ical_token": token_urlsafe(32),
            "is_active": "true"
        },
        {
            "username": "testmanager",
            "email": "manager@test.com",
            "full_name": "Test Manager",
            "role": UserRole.manager,
            "hashed_password": hashed_password,
            "ical_token": token_urlsafe(32),
            "is_active": "true"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user = User(**user_data)
        db.add(user)
        created_users.append(user)
    
    db.commit()
    
    # Refresh to get IDs
    for user in created_users:
        db.refresh(user)
    
    print(f"Created {len(created_users)} test users:")
    for user in created_users:
        print(f"  - {user.username} ({user.role.value}) - Password: {test_password}")
    
    return created_users

def create_test_employees(db: Session):
    """Create one employee of each type for testing"""
    print("Creating test employees...")
    
    # Common password for all test employees
    test_password = "TestPass123!"
    hashed_password = pwd_context.hash(test_password)
    
    # Create employees with different roles
    employees_data = [
        {
            "employee_id": "EMP001",
            "username": "testowner",
            "full_name": "Test Owner",
            "position": "Owner",
            "email": "owner@company.com",
            "phone": "+1234567890",
            "password_hash": hashed_password,
            "role": EmployeeRole.OWNER,
            "status": "active"
        },
        {
            "employee_id": "EMP002",
            "username": "testadmin",
            "full_name": "Test Admin",
            "position": "System Administrator",
            "email": "admin@company.com",
            "phone": "+1234567891",
            "password_hash": hashed_password,
            "role": EmployeeRole.ADMIN,
            "status": "active"
        },
        {
            "employee_id": "EMP003",
            "username": "testmanager",
            "full_name": "Test Manager",
            "position": "Operations Manager",
            "email": "manager@company.com",
            "phone": "+1234567892",
            "password_hash": hashed_password,
            "role": EmployeeRole.MANAGER,
            "status": "active"
        }
    ]
    
    created_employees = []
    for emp_data in employees_data:
        employee = Employee(**emp_data)
        db.add(employee)
        created_employees.append(employee)
    
    db.commit()
    
    # Refresh to get IDs
    for employee in created_employees:
        db.refresh(employee)
    
    print(f"Created {len(created_employees)} test employees:")
    for employee in created_employees:
        print(f"  - {employee.full_name} ({employee.position}) - Email: {employee.email} - Password: {test_password}")
    
    return created_employees

def main():
    """Main function to clear and create test users"""
    print("=== Test User Creation Script ===")
    
    # Get database session
    db = get_db_session()
    
    try:
        # Clear all existing data
        clear_all_data(db)
        
        # Create test users
        users = create_test_users(db)
        
        # Create test employees
        employees = create_test_employees(db)
        
        print("\n=== Summary ===")
        print(f"Created {len(users)} users and {len(employees)} employees for testing")
        print("\nUser credentials (for testing CRM functions):")
        for user in users:
            print(f"  {user.username}: TestPass123!")
        print("\nEmployee credentials (for testing administrative functions):")
        for employee in employees:
            print(f"  {employee.full_name}: {employee.email}")
        
        print("\nWARNING: These are test accounts. Do not use in production!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()