"""
Result pattern implementation for error handling in domain services.

This module provides a functional approach to error handling that makes
it easy to chain operations and handle both success and failure cases.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Generic, Optional, TypeVar, Union

T = TypeVar('T')
E = TypeVar('E', bound=Exception)


class Result(ABC, Generic[T, E]):
    """
    Result type for functional error handling.
    
    This is similar to Rust's Result<T, E> or Haskell's Either a b.
    It provides a clean way to handle both success and failure cases
    without throwing exceptions.
    """
    
    @abstractmethod
    def is_success(self) -> bool:
        """Check if the result is a success."""
        pass
    
    @abstractmethod
    def is_failure(self) -> bool:
        """Check if the result is a failure."""
        pass
    
    @abstractmethod
    def value(self) -> T:
        """Get the success value. Raises if failure."""
        pass
    
    @abstractmethod
    def error(self) -> E:
        """Get the error. Raises if success."""
        pass
    
    def map(self, func: Callable[[T], Any]) -> 'Result[Any, E]':
        """Apply function to success value if successful."""
        if self.is_success():
            try:
                return Success(func(self.value()))
            except Exception as e:
                return Failure(e)
        return self
    
    def flat_map(self, func: Callable[[T], 'Result[Any, E]']) -> 'Result[Any, E]':
        """Apply function that returns Result if successful."""
        if self.is_success():
            return func(self.value())
        return self
    
    def on_success(self, func: Callable[[T], None]) -> 'Result[T, E]':
        """Execute function if successful. Returns self for chaining."""
        if self.is_success():
            func(self.value())
        return self
    
    def on_failure(self, func: Callable[[E], None]) -> 'Result[T, E]':
        """Execute function if failure. Returns self for chaining."""
        if self.is_failure():
            func(self.error())
        return self
    
    def or_else(self, default: T) -> T:
        """Return success value or default if failure."""
        return self.value() if self.is_success() else default
    
    def or_else_get(self, default_func: Callable[[], T]) -> T:
        """Return success value or computed default if failure."""
        return self.value() if self.is_success() else default_func()
    
    def or_else_raise(self, exception_func: Callable[[E], Exception]) -> T:
        """Return success value or raise exception if failure."""
        if self.is_success():
            return self.value()
        raise exception_func(self.error())


@dataclass
class Success(Result[T, E]):
    """Successful result containing a value."""
    _value: T
    
    def is_success(self) -> bool:
        return True
    
    def is_failure(self) -> bool:
        return False
    
    def value(self) -> T:
        return self._value
    
    def error(self) -> E:
        raise ValueError("Cannot get error from Success result")


@dataclass
class Failure(Result[T, E]):
    """Failed result containing an error."""
    _error: E
    
    def is_success(self) -> bool:
        return False
    
    def is_failure(self) -> bool:
        return True
    
    def value(self) -> T:
        raise ValueError("Cannot get value from Failure result")
    
    def error(self) -> E:
        return self._error


# Convenience functions
def success(value: T) -> Result[T, Any]:
    """Create a successful result."""
    return Success(value)


def failure(error: E) -> Result[Any, E]:
    """Create a failed result."""
    return Failure(error)


# Type aliases for common use cases
ResultT = Result[T, Exception]
ResultStr = Result[str, Exception]
ResultInt = Result[int, Exception]
ResultBool = Result[bool, Exception]


# Domain-specific error classes
class DomainError(Exception):
    """Base class for domain-specific errors."""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}
    
    def to_dict(self) -> dict:
        """Convert error to dictionary for API responses."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "code": self.code,
            "details": self.details
        }


class ValidationError(DomainError):
    """Error raised when validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message, "VALIDATION_ERROR", {"field": field, "value": value})


class BusinessRuleError(DomainError):
    """Error raised when business rules are violated."""
    
    def __init__(self, message: str, rule: Optional[str] = None):
        super().__init__(message, "BUSINESS_RULE_VIOLATION", {"rule": rule})


class NotFoundError(DomainError):
    """Error raised when a resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            f"{resource_type} with id {resource_id} not found",
            "NOT_FOUND",
            {"resource_type": resource_type, "resource_id": resource_id}
        )


class ConflictError(DomainError):
    """Error raised when there's a conflict with existing data."""
    
    def __init__(self, message: str, conflicting_field: Optional[str] = None):
        super().__init__(message, "CONFLICT", {"conflicting_field": conflicting_field})


class PermissionError(DomainError):
    """Error raised when user lacks permission to perform an action."""
    
    def __init__(self, action: str, resource: str, required_permission: Optional[str] = None):
        super().__init__(
            f"Insufficient permission to {action} {resource}",
            "PERMISSION_DENIED",
            {"action": action, "resource": resource, "required_permission": required_permission}
        )


# Booking-specific errors
class BookingError(DomainError):
    """Base class for booking-related errors."""
    pass


class TimeSlotUnavailableError(BookingError):
    """Error raised when requested time slot is not available."""
    
    def __init__(self, start_time: str, end_time: str):
        super().__init__(
            f"Time slot {start_time} - {end_time} is not available",
            "TIME_SLOT_UNAVAILABLE",
            {"start_time": start_time, "end_time": end_time}
        )


class InvalidTimeSlotError(BookingError):
    """Error raised when time slot is invalid."""
    
    def __init__(self, message: str):
        super().__init__(message, "INVALID_TIME_SLOT")


class BookingNotFoundError(NotFoundError):
    """Error raised when booking is not found."""
    
    def __init__(self, booking_id: Any):
        super().__init__("Booking", booking_id)


# Employee-specific errors
class EmployeeError(DomainError):
    """Base class for employee-related errors."""
    pass


class AuthenticationError(EmployeeError):
    """Error raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_FAILED")


class InvalidCredentialsError(AuthenticationError):
    """Error raised when credentials are invalid."""
    
    def __init__(self):
        super().__init__("Invalid username or password")


class AccountLockedError(AuthenticationError):
    """Error raised when account is locked."""
    
    def __init__(self, locked_until: str):
        super().__init__(
            f"Account is locked until {locked_until}",
            "ACCOUNT_LOCKED",
            {"locked_until": locked_until}
        )


class RateLimitError(EmployeeError):
    """Error raised when rate limit is exceeded."""
    
    def __init__(self, retry_after: int):
        super().__init__(
            f"Rate limit exceeded. Try again in {retry_after} seconds",
            "RATE_LIMITED",
            {"retry_after": retry_after}
        )


# Utility functions for working with Results
def safe_call(func: Callable, *args, **kwargs) -> Result[Any, Exception]:
    """Safely call a function and return Result."""
    try:
        result = func(*args, **kwargs)
        return success(result)
    except Exception as e:
        return failure(e)


async def safe_async_call(func: Callable, *args, **kwargs) -> Result[Any, Exception]:
    """Safely call an async function and return Result."""
    try:
        result = await func(*args, **kwargs)
        return success(result)
    except Exception as e:
        return failure(e)


def combine_results(*results: Result[Any, Any]) -> Result[list, Any]:
    """Combine multiple results into a single result."""
    if all(r.is_success() for r in results):
        return success([r.value() for r in results])
    
    # Return first failure
    for result in results:
        if result.is_failure():
            return failure(result.error())
    
    return success([])


# Example usage:
# def create_booking(data: dict) -> Result[Booking, BookingError]:
#     # Validate data
#     validation_result = validate_booking_data(data)
#     if validation_result.is_failure():
#         return validation_result
#     
#     # Check availability
#     availability_result = check_availability(data)
#     if availability_result.is_failure():
#         return availability_result
#     
#     # Create booking
#     try:
#         booking = Booking.create(data)
#         return success(booking)
#     except Exception as e:
#         return failure(BookingError(f"Failed to create booking: {e}"))
