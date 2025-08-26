"""
Input validation and XSS protection for phStudio.
Enterprise-grade security using only Python standard library.
Cost-effective solution with zero additional dependencies.
"""

import re
import html
import json
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from urllib.parse import urlparse, parse_qs
import unicodedata

logger = logging.getLogger(__name__)


class InputValidator:
    """
    Comprehensive input validation and sanitization.
    Protects against XSS, SQL injection, and other attacks.
    """
    
    def __init__(self):
        # XSS patterns to detect and remove
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'onclick\s*=',
            r'onmouseover\s*=',
            r'onfocus\s*=',
            r'onblur\s*=',
            r'onchange\s*=',
            r'onsubmit\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
            r'<form[^>]*>.*?</form>',
            r'<input[^>]*>',
            r'<link[^>]*>',
            r'<meta[^>]*>',
            r'document\.cookie',
            r'document\.write',
            r'window\.location',
            r'eval\s*\(',
            r'expression\s*\(',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'union\s+select',
            r'drop\s+table',
            r'insert\s+into',
            r'delete\s+from',
            r'update\s+.*\s+set',
            r'create\s+table',
            r'alter\s+table',
            r'truncate\s+table',
            r'exec\s*\(',
            r'execute\s*\(',
            r'sp_executesql',
            r'xp_cmdshell',
            r'or\s+1\s*=\s*1',
            r'and\s+1\s*=\s*1',
            r"'\s*or\s*'.*'\s*=\s*'",
            r'--\s*$',
            r'/\*.*\*/',
        ]
        
        # Path traversal patterns
        self.path_traversal_patterns = [
            r'\.\./+',
            r'\.\.\\+',
            r'~/',
            r'%2e%2e%2f',
            r'%2e%2e%5c',
            r'%c0%af',
            r'%c1%9c',
        ]
        
        # Validation rules for different field types
        self.validation_rules = {
            'email': {
                'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                'max_length': 254,
                'required': True
            },
            'phone': {
                'pattern': r'^\+?[\d\s\-\(\)]{7,20}$',
                'max_length': 20,
                'required': False
            },
            'username': {
                'pattern': r'^[a-zA-Z0-9_]{3,30}$',
                'max_length': 30,
                'min_length': 3,
                'required': True
            },
            'password': {
                'min_length': 8,
                'max_length': 128,
                'required': True
            },
            'name': {
                'pattern': r'^[a-zA-Zа-яА-Я\s\-\.]{1,100}$',
                'max_length': 100,
                'min_length': 1,
                'required': True
            },
            'text': {
                'max_length': 1000,
                'required': False
            },
            'url': {
                'pattern': r'^https?://[^\s/$.?#].[^\s]*$',
                'max_length': 2048,
                'required': False
            },
            'numeric': {
                'pattern': r'^\d+$',
                'required': False
            },
            'decimal': {
                'pattern': r'^\d+(\.\d{1,2})?$',
                'required': False
            }
        }
    
    def sanitize_input(self, value: Any, field_type: str = 'text') -> str:
        """
        Sanitize input value to prevent XSS and other attacks.
        
        Args:
            value: Input value to sanitize
            field_type: Type of field for specific sanitization rules
            
        Returns:
            Sanitized string value
        """
        if value is None:
            return ""
        
        # Convert to string
        str_value = str(value)
        
        # Unicode normalization to prevent unicode-based attacks
        str_value = unicodedata.normalize('NFKC', str_value)
        
        # Remove null bytes and control characters
        str_value = ''.join(char for char in str_value if ord(char) >= 32 or char in '\t\n\r')
        
        # HTML encode to prevent XSS
        str_value = html.escape(str_value, quote=True)
        
        # Remove potentially dangerous patterns
        for pattern in self.xss_patterns:
            str_value = re.sub(pattern, '', str_value, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns (basic protection)
        for pattern in self.sql_patterns:
            str_value = re.sub(pattern, '', str_value, flags=re.IGNORECASE)
        
        # Remove path traversal patterns
        for pattern in self.path_traversal_patterns:
            str_value = re.sub(pattern, '', str_value, flags=re.IGNORECASE)
        
        # Field-specific sanitization
        if field_type == 'email':
            str_value = str_value.lower().strip()
        elif field_type == 'phone':
            # Keep only digits, spaces, dashes, parentheses, and plus
            str_value = re.sub(r'[^\d\s\-\(\)\+]', '', str_value)
        elif field_type == 'url':
            # Basic URL validation and sanitization
            try:
                parsed = urlparse(str_value)
                if parsed.scheme not in ['http', 'https']:
                    str_value = ''
            except:
                str_value = ''
        
        return str_value.strip()
    
    def validate_field(self, value: Any, field_type: str, field_name: str = '') -> tuple[bool, str]:
        """
        Validate a field value against its type rules.
        
        Args:
            value: Value to validate
            field_type: Type of field
            field_name: Name of field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if field_type not in self.validation_rules:
            return True, ""
        
        rules = self.validation_rules[field_type]
        str_value = str(value) if value is not None else ""
        
        # Required field check
        if rules.get('required', False) and not str_value.strip():
            return False, f"{field_name or 'Field'} is required"
        
        # Skip other validations if field is empty and not required
        if not str_value.strip() and not rules.get('required', False):
            return True, ""
        
        # Length validations
        if 'min_length' in rules and len(str_value) < rules['min_length']:
            return False, f"{field_name or 'Field'} must be at least {rules['min_length']} characters"
        
        if 'max_length' in rules and len(str_value) > rules['max_length']:
            return False, f"{field_name or 'Field'} must not exceed {rules['max_length']} characters"
        
        # Pattern validation
        if 'pattern' in rules and not re.match(rules['pattern'], str_value):
            return False, f"{field_name or 'Field'} format is invalid"
        
        return True, ""
    
    def validate_dict(self, data: Dict[str, Any], field_rules: Dict[str, str]) -> tuple[bool, Dict[str, str]]:
        """
        Validate a dictionary of values.
        
        Args:
            data: Dictionary of field values
            field_rules: Dictionary mapping field names to their types
            
        Returns:
            Tuple of (all_valid, errors_dict)
        """
        errors = {}
        all_valid = True
        
        for field_name, field_type in field_rules.items():
            value = data.get(field_name)
            is_valid, error_msg = self.validate_field(value, field_type, field_name)
            
            if not is_valid:
                errors[field_name] = error_msg
                all_valid = False
        
        return all_valid, errors
    
    def sanitize_dict(self, data: Dict[str, Any], field_rules: Dict[str, str]) -> Dict[str, Any]:
        """
        Sanitize all values in a dictionary.
        
        Args:
            data: Dictionary to sanitize
            field_rules: Dictionary mapping field names to their types
            
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for field_name, value in data.items():
            field_type = field_rules.get(field_name, 'text')
            sanitized[field_name] = self.sanitize_input(value, field_type)
        
        return sanitized
    
    def is_suspicious_input(self, value: str) -> bool:
        """
        Check if input contains suspicious patterns.
        
        Args:
            value: Input value to check
            
        Returns:
            True if input is suspicious
        """
        if not value:
            return False
        
        value_lower = value.lower()
        
        # Check for XSS patterns
        for pattern in self.xss_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE | re.DOTALL):
                return True
        
        # Check for SQL injection patterns
        for pattern in self.sql_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        # Check for path traversal
        for pattern in self.path_traversal_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        # Check for excessive length (potential buffer overflow)
        if len(value) > 10000:
            return True
        
        # Check for excessive special characters
        special_char_count = len(re.findall(r'[<>\'";%&\(\)\[\]{}]', value))
        if special_char_count > len(value) * 0.3:  # More than 30% special chars
            return True
        
        return False
    
    def log_suspicious_input(self, value: str, field_name: str, client_ip: str = "unknown"):
        """Log suspicious input for security monitoring"""
        logger.warning(
            f"Suspicious input detected",
            extra={
                "field_name": field_name,
                "client_ip": client_ip,
                "input_length": len(value),
                "input_preview": value[:100] if len(value) > 100 else value,
                "event_type": "suspicious_input"
            }
        )


class CSRFProtection:
    """
    CSRF token generation and validation.
    Simple implementation using Python secrets module.
    """
    
    def __init__(self):
        import secrets
        self.secret_key = secrets.token_urlsafe(32)
        self.token_cache = {}  # In production, use Redis or database
        self.token_lifetime = 3600  # 1 hour
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session"""
        import secrets
        import time
        
        token = secrets.token_urlsafe(32)
        self.token_cache[token] = {
            'session_id': session_id,
            'created_at': time.time()
        }
        
        # Clean up old tokens
        self._cleanup_expired_tokens()
        
        return token
    
    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token"""
        import time
        
        if not token or token not in self.token_cache:
            return False
        
        token_data = self.token_cache[token]
        
        # Check if token belongs to the session
        if token_data['session_id'] != session_id:
            return False
        
        # Check if token is expired
        if time.time() - token_data['created_at'] > self.token_lifetime:
            del self.token_cache[token]
            return False
        
        return True
    
    def _cleanup_expired_tokens(self):
        """Remove expired tokens from cache"""
        import time
        
        current_time = time.time()
        expired_tokens = [
            token for token, data in self.token_cache.items()
            if current_time - data['created_at'] > self.token_lifetime
        ]
        
        for token in expired_tokens:
            del self.token_cache[token]


class FileUploadValidator:
    """
    Secure file upload validation.
    Prevents malicious file uploads.
    """
    
    def __init__(self):
        # Allowed file extensions and MIME types
        self.allowed_extensions = {
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp'],
            'document': ['.pdf', '.doc', '.docx', '.txt'],
            'archive': ['.zip', '.rar']
        }
        
        self.allowed_mime_types = {
            'image': ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
            'document': ['application/pdf', 'application/msword', 'text/plain'],
            'archive': ['application/zip', 'application/x-rar-compressed']
        }
        
        # Maximum file sizes (in bytes)
        self.max_file_sizes = {
            'image': 5 * 1024 * 1024,  # 5MB
            'document': 10 * 1024 * 1024,  # 10MB
            'archive': 50 * 1024 * 1024  # 50MB
        }
        
        # Dangerous file patterns
        self.dangerous_patterns = [
            b'<?php',
            b'<script',
            b'javascript:',
            b'exec(',
            b'eval(',
            b'system(',
            b'shell_exec('
        ]
    
    def validate_file(self, file_data: bytes, filename: str, file_type: str = 'image') -> tuple[bool, str]:
        """
        Validate uploaded file.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            file_type: Type category (image, document, archive)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file type
        if file_type not in self.allowed_extensions:
            return False, "Invalid file type category"
        
        # Check file extension
        file_ext = self._get_file_extension(filename)
        if file_ext not in self.allowed_extensions[file_type]:
            return False, f"File extension {file_ext} not allowed for {file_type}"
        
        # Check file size
        if len(file_data) > self.max_file_sizes[file_type]:
            max_size_mb = self.max_file_sizes[file_type] / (1024 * 1024)
            return False, f"File size exceeds {max_size_mb}MB limit"
        
        # Check for dangerous content
        for pattern in self.dangerous_patterns:
            if pattern in file_data:
                return False, "File contains potentially dangerous content"
        
        # Validate file header (magic bytes)
        if not self._validate_file_header(file_data, file_ext):
            return False, "File header does not match extension"
        
        return True, ""
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension in lowercase"""
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    def _validate_file_header(self, file_data: bytes, extension: str) -> bool:
        """Validate file header matches extension"""
        if len(file_data) < 10:
            return False
        
        header = file_data[:10]
        
        # Magic bytes for common file types
        magic_bytes = {
            'jpg': [b'\xff\xd8\xff'],
            'jpeg': [b'\xff\xd8\xff'],
            'png': [b'\x89PNG\r\n\x1a\n'],
            'gif': [b'GIF87a', b'GIF89a'],
            'pdf': [b'%PDF'],
            'zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08']
        }
        
        if extension in magic_bytes:
            return any(header.startswith(magic) for magic in magic_bytes[extension])
        
        return True  # Unknown extension, assume valid


# Global instances for cost-effective singleton pattern
input_validator = InputValidator()
csrf_protection = CSRFProtection()
file_upload_validator = FileUploadValidator()


# Utility functions for easy access
def sanitize_user_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize user input data"""
    field_rules = {
        'username': 'username',
        'email': 'email',
        'full_name': 'name',
        'phone': 'phone',
        'password': 'password'
    }
    return input_validator.sanitize_dict(data, field_rules)


def sanitize_booking_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Sanitize booking input data"""
    field_rules = {
        'client_name': 'name',
        'client_phone': 'phone',
        'notes': 'text',
        'total_price': 'decimal'
    }
    
    sanitized = input_validator.sanitize_dict(data, field_rules)
    
    # Handle optional client_email separately
    if 'client_email' in data:
        client_email = data['client_email']
        if client_email:  # Only sanitize if not None/empty
            sanitized['client_email'] = input_validator.sanitize_input(client_email, 'email')
        else:
            sanitized['client_email'] = None
    
    return sanitized


def validate_user_input(data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
    """Validate user input data"""
    field_rules = {
        'username': 'username',
        'email': 'email',
        'full_name': 'name',
        'password': 'password'
    }
    return input_validator.validate_dict(data, field_rules)


def validate_booking_input(data: Dict[str, Any]) -> tuple[bool, Dict[str, str]]:
    """Validate booking input data"""
    field_rules = {
        'client_name': 'name',
        'client_phone': 'phone',
        'notes': 'text',
        'total_price': 'decimal'
    }
    
    # Special handling for optional client_email
    errors = {}
    all_valid = True
    
    # Validate required fields
    for field_name, field_type in field_rules.items():
        value = data.get(field_name)
        is_valid, error_msg = input_validator.validate_field(value, field_type, field_name)
        
        if not is_valid:
            errors[field_name] = error_msg
            all_valid = False
    
    # Validate optional email field
    client_email = data.get('client_email')
    if client_email and client_email.strip():  # Only validate if provided
        email_valid, email_error = input_validator.validate_field(client_email, 'email', 'client_email')
        # Override the required check for email in booking context
        if not email_valid and 'required' not in email_error:
            errors['client_email'] = email_error
            all_valid = False
    
    return all_valid, errors