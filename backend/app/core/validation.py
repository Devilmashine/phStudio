from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)

@dataclass
class ValidationError:
    """Validation error details"""
    field: str
    message: str
    code: str

class ValidationResult:
    """Result of validation operation"""
    
    def __init__(self, errors: List[ValidationError] = None):
        self.errors = errors or []
    
    def add_error(self, field: str, message: str, code: str):
        """Add a validation error"""
        self.errors.append(ValidationError(field, message, code))
    
    def is_valid(self) -> bool:
        """Check if validation passed"""
        return len(self.errors) == 0
    
    def get_errors(self) -> List[ValidationError]:
        """Get validation errors"""
        return self.errors
    
    def get_error_messages(self) -> List[str]:
        """Get validation error messages"""
        return [error.message for error in self.errors]

class Validator:
    """Base validator class"""
    
    def __init__(self):
        self.result = ValidationResult()
    
    def validate_required(self, value: Any, field_name: str) -> bool:
        """Validate that a field is required"""
        if value is None or (isinstance(value, str) and value.strip() == ""):
            self.result.add_error(
                field_name, 
                f"{field_name} is required", 
                f"{field_name}_required"
            )
            return False
        return True
    
    def validate_min_length(self, value: str, min_length: int, field_name: str) -> bool:
        """Validate minimum length"""
        if value and len(value) < min_length:
            self.result.add_error(
                field_name,
                f"{field_name} must be at least {min_length} characters long",
                f"{field_name}_min_length"
            )
            return False
        return True
    
    def validate_max_length(self, value: str, max_length: int, field_name: str) -> bool:
        """Validate maximum length"""
        if value and len(value) > max_length:
            self.result.add_error(
                field_name,
                f"{field_name} must be no more than {max_length} characters long",
                f"{field_name}_max_length"
            )
            return False
        return True
    
    def validate_email(self, email: str, field_name: str) -> bool:
        """Validate email format"""
        if email:
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(pattern, email):
                self.result.add_error(
                    field_name,
                    f"{field_name} must be a valid email address",
                    f"{field_name}_invalid_email"
                )
                return False
        return True
    
    def validate_phone(self, phone: str, field_name: str) -> bool:
        """Validate phone number format (E.164)"""
        if phone:
            # E.164 format: + followed by 10-15 digits
            pattern = r'^\+[1-9]\d{10,14}$'
            if not re.match(pattern, phone):
                self.result.add_error(
                    field_name,
                    f"{field_name} must be a valid phone number in E.164 format (+1234567890)",
                    f"{field_name}_invalid_phone"
                )
                return False
        return True
    
    def validate_datetime(self, date_str: str, field_name: str) -> bool:
        """Validate datetime format"""
        if date_str:
            try:
                datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                self.result.add_error(
                    field_name,
                    f"{field_name} must be a valid ISO datetime",
                    f"{field_name}_invalid_datetime"
                )
                return False
        return True
    
    def validate_enum(self, value: str, valid_values: List[str], field_name: str) -> bool:
        """Validate enum value"""
        if value and value not in valid_values:
            self.result.add_error(
                field_name,
                f"{field_name} must be one of: {', '.join(valid_values)}",
                f"{field_name}_invalid_enum"
            )
            return False
        return True

class BookingValidator(Validator):
    """Validator for booking data"""
    
    def validate_booking_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate booking data"""
        # Reset validation result
        self.result = ValidationResult()
        
        # Required fields
        self.validate_required(data.get('client_name'), 'client_name')
        self.validate_required(data.get('client_phone'), 'client_phone')
        self.validate_required(data.get('booking_date'), 'booking_date')
        self.validate_required(data.get('start_time'), 'start_time')
        self.validate_required(data.get('end_time'), 'end_time')
        self.validate_required(data.get('space_type'), 'space_type')
        
        # Field lengths
        if 'client_name' in data:
            self.validate_min_length(data['client_name'], 2, 'client_name')
            self.validate_max_length(data['client_name'], 200, 'client_name')
        
        if 'client_phone' in data:
            self.validate_phone(data['client_phone'], 'client_phone')
        
        if 'client_email' in data and data['client_email']:
            self.validate_email(data['client_email'], 'client_email')
            self.validate_max_length(data['client_email'], 255, 'client_email')
        
        if 'space_type' in data:
            self.validate_max_length(data['space_type'], 50, 'space_type')
        
        if 'special_requirements' in data and data['special_requirements']:
            self.validate_max_length(data['special_requirements'], 1000, 'special_requirements')
        
        # Price validation
        if 'base_price' in data:
            if not isinstance(data['base_price'], (int, float)) or data['base_price'] < 0:
                self.result.add_error(
                    'base_price',
                    'base_price must be a non-negative number',
                    'base_price_invalid'
                )
        
        if 'total_price' in data:
            if not isinstance(data['total_price'], (int, float)) or data['total_price'] < 0:
                self.result.add_error(
                    'total_price',
                    'total_price must be a non-negative number',
                    'total_price_invalid'
                )
        
        # Date/time validation
        if 'booking_date' in data:
            self.validate_datetime(data['booking_date'], 'booking_date')
        
        if 'start_time' in data:
            self.validate_datetime(data['start_time'], 'start_time')
        
        if 'end_time' in data:
            self.validate_datetime(data['end_time'], 'end_time')
        
        # Time logic validation
        if 'start_time' in data and 'end_time' in data:
            try:
                start_dt = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
                
                if start_dt >= end_dt:
                    self.result.add_error(
                        'time_range',
                        'Start time must be before end time',
                        'invalid_time_range'
                    )
            except ValueError:
                # DateTime validation will catch this
                pass
        
        return self.result

class EmployeeValidator(Validator):
    """Validator for employee data"""
    
    def validate_employee_data(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate employee data"""
        # Reset validation result
        self.result = ValidationResult()
        
        # Required fields
        self.validate_required(data.get('full_name'), 'full_name')
        self.validate_required(data.get('username'), 'username')
        self.validate_required(data.get('email'), 'email')
        self.validate_required(data.get('password'), 'password')
        self.validate_required(data.get('role'), 'role')
        
        # Field lengths
        if 'full_name' in data:
            self.validate_min_length(data['full_name'], 2, 'full_name')
            self.validate_max_length(data['full_name'], 200, 'full_name')
        
        if 'username' in data:
            self.validate_min_length(data['username'], 3, 'username')
            self.validate_max_length(data['username'], 50, 'username')
        
        if 'email' in data:
            self.validate_email(data['email'], 'email')
            self.validate_max_length(data['email'], 255, 'email')
        
        if 'password' in data:
            self.validate_min_length(data['password'], 8, 'password')
        
        if 'phone' in data and data['phone']:
            self.validate_phone(data['phone'], 'phone')
        
        if 'department' in data and data['department']:
            self.validate_max_length(data['department'], 50, 'department')
        
        # Role validation
        valid_roles = ['owner', 'admin', 'manager']
        if 'role' in data:
            self.validate_enum(data['role'], valid_roles, 'role')
        
        return self.result