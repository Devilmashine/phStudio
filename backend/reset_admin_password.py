#!/usr/bin/env python3
"""
Script to reset the admin password to a known valid password.
This script is for administrative purposes only.
"""

import os
import sys
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.core.database import get_engine, get_session_local
from app.models.user import User

# Password context for hashing (same as in user service)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)

def get_db_session():
    """Get database session"""
    engine = get_engine()
    SessionLocal = get_session_local()
    return SessionLocal()

def reset_admin_password(db: Session):
    """Reset the admin password to a known valid password"""
    # Find the admin user
    user = db.query(User).filter(User.username == "admin").first()
    
    if not user:
        print("Admin user not found.")
        return False
    
    # Use a known valid password that passes all validation rules
    new_password = "StudioPass!A9B8C7"
    
    # Hash and set the new password using the same method as in UserService
    hashed_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_password
    
    # Commit the changes
    db.commit()
    
    print(f"Password successfully reset for admin user.")
    print(f"New password: {new_password}")
    return True

def main():
    """Main function to reset the admin password"""
    print("=== Admin Password Reset Script ===")
    
    # Get database session
    db = get_db_session()
    
    try:
        # Reset the admin password
        success = reset_admin_password(db)
        
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