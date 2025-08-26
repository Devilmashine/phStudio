"""
Centralized error handling for phStudio application.

This module provides consistent error handling patterns and custom exceptions
for better error management and user experience.
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class PhStudioError(Exception):
    """Base exception class for phStudio application"""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class BookingError(PhStudioError):
    """Exception raised for booking-related errors"""
    pass


class AuthenticationError(PhStudioError):
    """Exception raised for authentication-related errors"""
    pass


class AuthorizationError(PhStudioError):
    """Exception raised for authorization-related errors"""
    pass


class ValidationError(PhStudioError):
    """Exception raised for validation-related errors"""
    pass


class ServiceError(PhStudioError):
    """Exception raised for service-related errors"""
    pass


def handle_database_error(error: SQLAlchemyError, operation: str) -> HTTPException:
    """
    Handle database errors and convert them to appropriate HTTP exceptions.
    
    Args:
        error: The SQLAlchemy error that occurred
        operation: Description of the operation that failed
        
    Returns:
        HTTPException with appropriate status code and message
    """
    logger.error(f"Database error during {operation}: {error}")
    
    if isinstance(error, IntegrityError):
        # Handle constraint violations
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "INTEGRITY_ERROR",
                "message": "Данная операция нарушает ограничения базы данных",
                "operation": operation
            }
        )
    
    # Generic database error
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "DATABASE_ERROR",
            "message": "Ошибка базы данных",
            "operation": operation
        }
    )


def handle_validation_error(error: ValidationError, field: str = None) -> HTTPException:
    """
    Handle validation errors and convert them to HTTP exceptions.
    
    Args:
        error: The validation error that occurred
        field: Optional field name that caused the error
        
    Returns:
        HTTPException with validation error details
    """
    logger.warning(f"Validation error for field {field}: {error}")
    
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={
            "error": "VALIDATION_ERROR",
            "message": "Ошибка валидации данных",
            "field": field,
            "details": str(error)
        }
    )


def handle_not_found_error(resource: str, identifier: Any) -> HTTPException:
    """
    Handle not found errors.
    
    Args:
        resource: Type of resource that was not found
        identifier: Identifier that was searched for
        
    Returns:
        HTTPException with not found error
    """
    logger.info(f"{resource} not found: {identifier}")
    
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail={
            "error": "NOT_FOUND",
            "message": f"{resource} не найден",
            "resource": resource,
            "identifier": str(identifier)
        }
    )


def handle_authorization_error(operation: str, user_role: str = None) -> HTTPException:
    """
    Handle authorization errors.
    
    Args:
        operation: Operation that was attempted
        user_role: User's role (if available)
        
    Returns:
        HTTPException with authorization error
    """
    logger.warning(f"Authorization denied for operation {operation}, user role: {user_role}")
    
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "error": "AUTHORIZATION_ERROR",
            "message": "Недостаточно прав для выполнения операции",
            "operation": operation,
            "required_role": "admin или manager"
        }
    )


def handle_authentication_error(reason: str = None) -> HTTPException:
    """
    Handle authentication errors.
    
    Args:
        reason: Optional reason for authentication failure
        
    Returns:
        HTTPException with authentication error
    """
    logger.info(f"Authentication failed: {reason}")
    
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": "AUTHENTICATION_ERROR",
            "message": "Ошибка аутентификации",
            "reason": reason
        },
        headers={"WWW-Authenticate": "Bearer"},
    )


def handle_service_error(service: str, operation: str, error: Exception) -> HTTPException:
    """
    Handle service-specific errors.
    
    Args:
        service: Name of the service
        operation: Operation that failed
        error: The original exception
        
    Returns:
        HTTPException with service error details
    """
    logger.error(f"Service error in {service}.{operation}: {error}")
    
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail={
            "error": "SERVICE_ERROR",
            "message": f"Ошибка в сервисе {service}",
            "operation": operation,
            "service": service
        }
    )


def create_error_response(
    error_code: str,
    message: str,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    details: Optional[Dict[str, Any]] = None
) -> HTTPException:
    """
    Create a standardized error response.
    
    Args:
        error_code: Unique error code
        message: Human-readable error message
        status_code: HTTP status code
        details: Additional error details
        
    Returns:
        HTTPException with standardized error structure
    """
    error_detail = {
        "error": error_code,
        "message": message
    }
    
    if details:
        error_detail.update(details)
    
    return HTTPException(
        status_code=status_code,
        detail=error_detail
    )


class ErrorHandler:
    """Context manager for handling errors in service operations"""
    
    def __init__(self, operation: str, service: str = "unknown"):
        self.operation = operation
        self.service = service
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            return False
        
        if isinstance(exc_val, PhStudioError):
            # Re-raise custom errors
            return False
        elif isinstance(exc_val, SQLAlchemyError):
            raise handle_database_error(exc_val, self.operation)
        elif isinstance(exc_val, ValidationError):
            raise handle_validation_error(exc_val)
        else:
            raise handle_service_error(self.service, self.operation, exc_val)