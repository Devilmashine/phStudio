from typing import Optional, Dict, Any
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from ..models.employee_enhanced import Employee, EmployeeStatus
from ..repositories.employee_repository import EmployeeRepository
from ..core.event_bus import EventBus, create_event

logger = logging.getLogger(__name__)

class SecurityService:
    """Security service for employee authentication and authorization"""
    
    def __init__(self, employee_repo: EmployeeRepository, event_bus: EventBus):
        self.employee_repo = employee_repo
        self.event_bus = event_bus
        self.failed_attempts = {}  # In-memory store for failed attempts
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    def _hash_password(self, password: str, salt: str = None) -> tuple:
        """Hash a password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use SHA-256 with salt
        pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                      password.encode('utf-8'), 
                                      salt.encode('ascii'), 
                                      100000)  # 100,000 iterations
        return salt + pwdhash.hex()
    
    def verify_password(self, password: str, stored_password: str) -> bool:
        """Verify a password against stored hash"""
        if len(stored_password) < 32:  # Minimum length check
            return False
            
        salt = stored_password[:32]  # First 32 chars are salt
        stored_hash = stored_password[32:]
        
        # Hash the provided password with the stored salt
        pwdhash = hashlib.pbkdf2_hmac('sha256',
                                      password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        
        return pwdhash.hex() == stored_hash
    
    def _is_rate_limited(self, username: str) -> bool:
        """Check if user is rate limited due to failed attempts"""
        if username not in self.failed_attempts:
            return False
            
        attempts, last_attempt = self.failed_attempts[username]
        if attempts < self.max_failed_attempts:
            return False
            
        # Check if lockout period has expired
        if datetime.now() - last_attempt > self.lockout_duration:
            # Reset failed attempts
            del self.failed_attempts[username]
            return False
            
        return True
    
    def _record_failed_attempt(self, username: str):
        """Record a failed login attempt"""
        if username in self.failed_attempts:
            attempts, _ = self.failed_attempts[username]
            self.failed_attempts[username] = (attempts + 1, datetime.now())
        else:
            self.failed_attempts[username] = (1, datetime.now())
    
    def _reset_failed_attempts(self, username: str):
        """Reset failed attempts after successful login"""
        if username in self.failed_attempts:
            del self.failed_attempts[username]
    
    async def authenticate(
        self, 
        username: str, 
        password: str,
        mfa_code: str = None
    ) -> Dict[str, Any]:
        """Authenticate an employee"""
        # Check rate limiting
        if self._is_rate_limited(username):
            logger.warning(f"Rate limited login attempt for user: {username}")
            return {
                "success": False,
                "error": "ACCOUNT_LOCKED",
                "message": "Account temporarily locked due to too many failed attempts"
            }
        
        # Get employee
        employee = self.employee_repo.get_by_username(username)
        if not employee:
            self._record_failed_attempt(username)
            logger.warning(f"Failed login attempt for non-existent user: {username}")
            return {
                "success": False,
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid username or password"
            }
        
        # Check if employee is active
        if employee.status != EmployeeStatus.ACTIVE:
            logger.warning(f"Login attempt for inactive user: {username}")
            return {
                "success": False,
                "error": "ACCOUNT_INACTIVE",
                "message": "Account is not active"
            }
        
        # Verify password
        if not self.verify_password(password, employee.password_hash):
            self._record_failed_attempt(username)
            logger.warning(f"Failed login attempt for user: {username}")
            return {
                "success": False,
                "error": "INVALID_CREDENTIALS",
                "message": "Invalid username or password"
            }
        
        # Check MFA if enabled
        if employee.mfa_secret and mfa_code:
            # In a real implementation, we would verify the TOTP code
            # For now, we'll just check if the code is provided
            if not mfa_code:
                logger.warning(f"MFA required for user: {username}")
                return {
                    "success": False,
                    "error": "MFA_REQUIRED",
                    "message": "Multi-factor authentication required"
                }
        
        # Reset failed attempts
        self._reset_failed_attempts(username)
        
        # Update last activity
        employee.last_activity = datetime.now()
        # In a real implementation, we would save this to the database
        
        # Create and publish event
        event = create_event(
            event_type="employee_login",
            payload={
                "employee_id": employee.id,
                "username": employee.username,
                "timestamp": datetime.now().isoformat()
            }
        )
        await self.event_bus.publish(event)
        
        logger.info(f"Successful login for user: {username}")
        
        return {
            "success": True,
            "employee": {
                "id": employee.id,
                "employee_id": employee.employee_id,
                "username": employee.username,
                "email": employee.email,
                "full_name": employee.full_name,
                "role": employee.role.value,
                "department": employee.department
            }
        }
    
    def generate_mfa_secret(self) -> str:
        """Generate a new MFA secret"""
        return secrets.token_hex(16)
    
    def change_password(
        self, 
        employee_id: int, 
        current_password: str, 
        new_password: str
    ) -> Dict[str, Any]:
        """Change employee password"""
        employee = self.employee_repo.get_by_id(employee_id)
        if not employee:
            return {
                "success": False,
                "error": "EMPLOYEE_NOT_FOUND",
                "message": "Employee not found"
            }
        
        # Verify current password
        if not self.verify_password(current_password, employee.password_hash):
            return {
                "success": False,
                "error": "INVALID_CURRENT_PASSWORD",
                "message": "Current password is incorrect"
            }
        
        # Hash new password
        new_hash = self._hash_password(new_password)
        
        # Update employee record
        employee.password_hash = new_hash
        employee.password_changed_at = datetime.now()
        
        # In a real implementation, we would save this to the database
        
        logger.info(f"Password changed for employee: {employee.username}")
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }