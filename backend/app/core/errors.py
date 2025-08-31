"""
Centralized error handling for phStudio application.

This module provides consistent error handling patterns and custom exceptions
for better error management and user experience.
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
import logging
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)

@dataclass
class AppError(Exception):
    """Base application error"""
    message: str
    error_code: str
    details: Optional[Dict[str, Any]] = None
    status_code: int = 500
    
    def __post_init__(self):
        super().__init__(self.message)

class ValidationError(AppError):
    """Validation error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 400)

class AuthenticationError(AppError):
    """Authentication error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 401)

class AuthorizationError(AppError):
    """Authorization error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 403)

class NotFoundError(AppError):
    """Resource not found error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 404)

class ConflictError(AppError):
    """Resource conflict error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 409)

class BusinessLogicError(AppError):
    """Business logic error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 422)

class ExternalServiceError(AppError):
    """External service error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 502)

class BookingError(AppError):
    """Booking-specific error"""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        super().__init__(message, error_code, details, 400)

class ErrorHandler:
    """Context manager for handling errors"""
    
    def __init__(self, operation: str, component: str):
        self.operation = operation
        self.component = component
    
    def __enter__(self):
        logger.debug(f"Starting operation: {self.operation} in {self.component}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(
                f"Error in {self.component}.{self.operation}: {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            logger.debug(f"Completed operation: {self.operation} in {self.component}")
        # Don't suppress the exception
        return False

# Error factory functions
def create_validation_error(field: str, message: str) -> ValidationError:
    """Create a validation error"""
    return ValidationError(
        message=message,
        error_code=f"validation_{field}",
        details={"field": field, "message": message}
    )

def create_authentication_error(message: str) -> AuthenticationError:
    """Create an authentication error"""
    return AuthenticationError(
        message=message,
        error_code="authentication_failed"
    )

def create_authorization_error(message: str) -> AuthorizationError:
    """Create an authorization error"""
    return AuthorizationError(
        message=message,
        error_code="authorization_failed"
    )

def create_not_found_error(resource: str, identifier: str) -> NotFoundError:
    """Create a not found error"""
    return NotFoundError(
        message=f"{resource} not found: {identifier}",
        error_code=f"{resource}_not_found",
        details={"resource": resource, "identifier": identifier}
    )

def create_conflict_error(resource: str, identifier: str, reason: str) -> ConflictError:
    """Create a conflict error"""
    return ConflictError(
        message=f"Conflict with {resource} {identifier}: {reason}",
        error_code=f"{resource}_conflict",
        details={"resource": resource, "identifier": identifier, "reason": reason}
    )

def create_business_logic_error(message: str, error_code: str) -> BusinessLogicError:
    """Create a business logic error"""
    return BusinessLogicError(
        message=message,
        error_code=error_code
    )

def create_external_service_error(service: str, message: str) -> ExternalServiceError:
    """Create an external service error"""
    return ExternalServiceError(
        message=f"External service error [{service}]: {message}",
        error_code=f"{service}_error",
        details={"service": service, "message": message}
    )

# Database error handlers
def handle_database_error(error: SQLAlchemyError, operation: str) -> AppError:
    """Convert SQLAlchemy errors to appropriate application errors"""
    error_msg = str(error.orig) if hasattr(error, 'orig') else str(error)
    
    # Handle specific database errors
    if "duplicate key" in error_msg.lower() or "unique constraint" in error_msg.lower():
        return ConflictError(
            message=f"Resource already exists",
            error_code="RESOURCE_EXISTS",
            details={"operation": operation, "error": error_msg}
        )
    elif "foreign key constraint" in error_msg.lower():
        return ValidationError(
            message=f"Invalid reference",
            error_code="INVALID_REFERENCE",
            details={"operation": operation, "error": error_msg}
        )
    elif "not null constraint" in error_msg.lower():
        return ValidationError(
            message=f"Required field missing",
            error_code="MISSING_REQUIRED_FIELD",
            details={"operation": operation, "error": error_msg}
        )
    else:
        return AppError(
            message=f"Database error during {operation}",
            error_code="DATABASE_ERROR",
            details={"operation": operation, "error": error_msg},
            status_code=500
        )

def handle_not_found_error(resource: str, identifier: str) -> NotFoundError:
    """Create a standardized not found error"""
    return create_not_found_error(resource, identifier)