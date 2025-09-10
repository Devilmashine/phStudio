#!/usr/bin/env python3
"""
Script to reset a user's password in the database.
This script is for administrative purposes only.
"""

import os
import sys
from sqlalchemy.orm import Session
from getpass import getpass
import re

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_engine, get_session_local
from app.models.user import User
from app.core.password_security import password_service

def get_db_session():
    """Get database session"""
    engine = get_engine()
    SessionLocal = get_session_local()
    return SessionLocal()

def validate_password(password: str) -> bool:
    """Validate password strength"""
    is_valid, errors = password_service.validate_password(password, "user")
    if not is_valid:
        print("Password validation errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    return True

def reset_user_password(db: Session, username: str, new_password: str):
    """Reset a user's password"""
    # Find the user
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        print(f"User '{username}' not found.")
        return False
    
    # Validate the new password
    if not validate_password(new_password):
        print("Password does not meet security requirements.")
        return False
    
    # Hash and set the new password
    hashed_password = password_service.hash_password(new_password)
    user.hashed_password = hashed_password
    
    # Commit the changes
    db.commit()
    
    print(f"Password successfully reset for user '{username}'.")
    return True

def main():
    """Main function to reset a user's password"""
    print("=== Password Reset Script ===")
    
    if len(sys.argv) != 2:
        print("Usage: python reset_user_password.py <username>")
        print("Example: python reset_user_password.py admin")
        sys.exit(1)
    
    username = sys.argv[1]
    
    # Get database session
    db = get_db_session()
    
    try:
        # Get the new password from user input
        print(f"Resetting password for user: {username}")
        new_password = getpass("Enter new password: ")
        confirm_password = getpass("Confirm new password: ")
        
        if new_password != confirm_password:
            print("Passwords do not match.")
            sys.exit(1)
        
        # Reset the password
        success = reset_user_password(db, username, new_password)
        
        if not success:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()