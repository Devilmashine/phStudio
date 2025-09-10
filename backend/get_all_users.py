#!/usr/bin/env python3
"""
Script to retrieve all users from the database with their login information.
This script is for administrative purposes only.
"""

import os
import sys
from sqlalchemy.orm import Session

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_engine, get_session_local
from app.models.user import User

def get_db_session():
    """Get database session"""
    engine = get_engine()
    SessionLocal = get_session_local()
    return SessionLocal()

def get_all_users(db: Session):
    """Retrieve all users from the database"""
    print("Retrieving all users from the database...")
    
    users = db.query(User).all()
    
    if not users:
        print("No users found in the database.")
        return []
    
    print(f"\nFound {len(users)} users:")
    print("-" * 80)
    print(f"{'ID':<5} {'Username':<15} {'Email':<25} {'Role':<10} {'Full Name':<20}")
    print("-" * 80)
    
    for user in users:
        print(f"{user.id:<5} {user.username:<15} {user.email:<25} {user.role.value:<10} {user.full_name or 'N/A':<20}")
    
    return users

def main():
    """Main function to retrieve all users"""
    print("=== User Retrieval Script ===")
    
    # Get database session
    db = get_db_session()
    
    try:
        # Retrieve all users
        users = get_all_users(db)
        
        if users:
            print(f"\n=== Detailed User Information ===")
            for user in users:
                print(f"\nUser ID: {user.id}")
                print(f"  Username: {user.username}")
                print(f"  Email: {user.email}")
                print(f"  Role: {user.role.value}")
                print(f"  Full Name: {user.full_name or 'N/A'}")
                print(f"  Phone: {user.phone or 'N/A'}")
                print(f"  Active: {user.is_active}")
                print(f"  Created At: {user.created_at}")
                print(f"  Last Login: {user.last_login or 'Never'}")
                # Note: We don't display hashed_password for security reasons
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()