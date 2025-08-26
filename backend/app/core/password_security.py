"""
Password security service for phStudio.
Enterprise-grade password validation with zero additional dependencies.
"""

import re
import hashlib
import secrets
import string
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PasswordSecurityService:
    """
    Comprehensive password security service.
    Uses only Python standard library for cost-effectiveness.
    """
    
    def __init__(self, 
                 min_length: int = 8,
                 require_uppercase: bool = True,
                 require_numbers: bool = True,
                 require_special: bool = True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        
        # Common weak passwords (basic list)
        self.weak_passwords = {
            "password", "password123", "123456", "qwerty", "abc123",
            "admin", "administrator", "root", "user", "guest",
            "password1", "123456789", "welcome", "login", "pass"
        }
        
        # Common leaked password patterns
        self.weak_patterns = [
            r"^password\d*$",
            r"^123+.*",
            r"^qwerty.*",
            r"^admin.*",
            r"^\w*123$"
        ]
    
    def validate_password(self, password: str, username: str = None) -> Tuple[bool, List[str]]:
        """
        Comprehensive password validation.
        Returns (is_valid, list_of_errors).
        """
        errors = []
        
        # Length check
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        # Character requirements
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if self.require_numbers and not re.search(r'\d', password):
            errors.append("Password must contain at least one number")
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        
        # Weakness checks
        if password.lower() in self.weak_passwords:
            errors.append("Password is too common and easily guessable")
        
        # Pattern checks
        for pattern in self.weak_patterns:
            if re.match(pattern, password.lower()):
                errors.append("Password matches a common weak pattern")
                break
        
        # Username similarity check
        if username and username.lower() in password.lower():
            errors.append("Password cannot contain username")
        
        # Sequential characters check
        if self._has_sequential_chars(password):
            errors.append("Password cannot contain sequential characters (123, abc, etc.)")
        
        # Repeated characters check
        if self._has_repeated_chars(password):
            errors.append("Password cannot have more than 2 consecutive repeated characters")
        
        return len(errors) == 0, errors
    
    def _has_sequential_chars(self, password: str) -> bool:
        """Check for sequential characters like 123, abc, etc."""
        password_lower = password.lower()
        
        # Check for numeric sequences
        for i in range(len(password_lower) - 2):
            if password_lower[i:i+3].isdigit():
                nums = [int(x) for x in password_lower[i:i+3]]
                if nums[1] == nums[0] + 1 and nums[2] == nums[1] + 1:
                    return True
        
        # Check for alphabetic sequences
        for i in range(len(password_lower) - 2):
            if password_lower[i:i+3].isalpha():
                chars = password_lower[i:i+3]
                if (ord(chars[1]) == ord(chars[0]) + 1 and 
                    ord(chars[2]) == ord(chars[1]) + 1):
                    return True
        
        return False
    
    def _has_repeated_chars(self, password: str) -> bool:
        """Check for excessive repeated characters"""
        for i in range(len(password) - 2):
            if password[i] == password[i+1] == password[i+2]:
                return True
        return False
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a cryptographically secure password"""
        if length < self.min_length:
            length = self.min_length
        
        # Character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*(),.?\":{}|<>"
        
        # Ensure at least one character from each required set
        password = []
        if self.require_uppercase:
            password.append(secrets.choice(uppercase))
        password.append(secrets.choice(lowercase))
        if self.require_numbers:
            password.append(secrets.choice(digits))
        if self.require_special:
            password.append(secrets.choice(special))
        
        # Fill the rest randomly
        all_chars = lowercase + uppercase + digits + special
        for _ in range(length - len(password)):
            password.append(secrets.choice(all_chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        
        return ''.join(password)
    
    def calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        char_space = 0
        
        if re.search(r'[a-z]', password):
            char_space += 26
        if re.search(r'[A-Z]', password):
            char_space += 26
        if re.search(r'\d', password):
            char_space += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            char_space += 18
        
        if char_space == 0:
            return 0.0
        
        import math
        return len(password) * math.log2(char_space)
    
    def get_password_strength(self, password: str) -> Tuple[str, int]:
        """
        Get password strength assessment.
        Returns (strength_label, score_out_of_100).
        """
        score = 0
        
        # Length score (up to 25 points)
        length_score = min(25, (len(password) / 16) * 25)
        score += length_score
        
        # Character diversity (up to 25 points)
        diversity_score = 0
        if re.search(r'[a-z]', password):
            diversity_score += 6
        if re.search(r'[A-Z]', password):
            diversity_score += 6
        if re.search(r'\d', password):
            diversity_score += 6
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            diversity_score += 7
        score += diversity_score
        
        # Entropy score (up to 25 points)
        entropy = self.calculate_entropy(password)
        entropy_score = min(25, (entropy / 80) * 25)
        score += entropy_score
        
        # Uniqueness score (up to 25 points)
        uniqueness_score = 25
        if password.lower() in self.weak_passwords:
            uniqueness_score -= 15
        for pattern in self.weak_patterns:
            if re.match(pattern, password.lower()):
                uniqueness_score -= 10
                break
        if self._has_sequential_chars(password):
            uniqueness_score -= 5
        if self._has_repeated_chars(password):
            uniqueness_score -= 5
        
        score += max(0, uniqueness_score)
        
        # Determine strength label
        if score < 25:
            return "Very Weak", int(score)
        elif score < 50:
            return "Weak", int(score)
        elif score < 70:
            return "Fair", int(score)
        elif score < 85:
            return "Good", int(score)
        else:
            return "Strong", int(score)


class AccountSecurityService:
    """
    Account security service for handling login attempts and lockouts.
    Uses in-memory storage for cost-effectiveness.
    """
    
    def __init__(self, max_attempts: int = 5, lockout_duration_minutes: int = 30):
        self.max_attempts = max_attempts
        self.lockout_duration = timedelta(minutes=lockout_duration_minutes)
        self.failed_attempts = {}  # ip -> {'count': int, 'last_attempt': datetime, 'locked_until': datetime}
    
    def record_failed_login(self, identifier: str) -> None:
        """Record a failed login attempt"""
        now = datetime.utcnow()
        
        if identifier not in self.failed_attempts:
            self.failed_attempts[identifier] = {
                'count': 1,
                'last_attempt': now,
                'locked_until': None
            }
        else:
            self.failed_attempts[identifier]['count'] += 1
            self.failed_attempts[identifier]['last_attempt'] = now
            
            # Lock account if max attempts reached
            if self.failed_attempts[identifier]['count'] >= self.max_attempts:
                self.failed_attempts[identifier]['locked_until'] = now + self.lockout_duration
                logger.warning(f"Account locked due to {self.max_attempts} failed login attempts: {identifier}")
    
    def record_successful_login(self, identifier: str) -> None:
        """Record a successful login and clear failed attempts"""
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    def is_locked(self, identifier: str) -> Tuple[bool, Optional[datetime]]:
        """
        Check if account is locked.
        Returns (is_locked, unlock_time).
        """
        if identifier not in self.failed_attempts:
            return False, None
        
        attempt_data = self.failed_attempts[identifier]
        locked_until = attempt_data.get('locked_until')
        
        if not locked_until:
            return False, None
        
        now = datetime.utcnow()
        if now >= locked_until:
            # Lockout expired, clear the entry
            del self.failed_attempts[identifier]
            return False, None
        
        return True, locked_until
    
    def get_remaining_attempts(self, identifier: str) -> int:
        """Get remaining attempts before lockout"""
        if identifier not in self.failed_attempts:
            return self.max_attempts
        
        failed_count = self.failed_attempts[identifier]['count']
        return max(0, self.max_attempts - failed_count)
    
    def cleanup_old_entries(self) -> None:
        """Clean up old entries to prevent memory leaks"""
        now = datetime.utcnow()
        cutoff_time = now - timedelta(hours=24)  # Remove entries older than 24 hours
        
        identifiers_to_remove = []
        for identifier, data in self.failed_attempts.items():
            if data['last_attempt'] < cutoff_time:
                identifiers_to_remove.append(identifier)
        
        for identifier in identifiers_to_remove:
            del self.failed_attempts[identifier]


# Global instances for cost-effective singleton pattern
password_service = PasswordSecurityService()
account_security_service = AccountSecurityService()