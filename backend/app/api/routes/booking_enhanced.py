"""
Enhanced Booking API with CQRS and Event Bus integration.

This module provides a comprehensive REST API for booking management
that follows FAANG engineering standards and implements domain-driven design.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ...core.result import Result, DomainError
from ...core.cqrs import (
    CreateBookingCommand, UpdateBookingCommand, CancelBookingCommand,
    TransitionBookingStateCommand, GetBookingQuery, GetBookingsForDateQuery
)
from ...core.event_bus import publish_event
from ...services.booking_domain_service import BookingDomainService
from ...models.booking_enhanced import BookingState, SpaceType, PaymentStatus
from ...models.employee_enhanced import Employee
from ...core.security import SecurityService, SecurityContext
from ...core.cache import get_cache_service, cached, cache_invalidate

router = APIRouter(prefix="/api/v1/bookings", tags=["bookings"])

# Pydantic models for API requests/responses
class CreateBookingRequest(BaseModel):
    """Request model for creating a booking."""
    client_name: str = Field(..., min_length=2, max_length=200, description="Client's full name")
    client_phone: str = Field(..., min_length=10, max_length=20, description="Client's phone number")
    client_email: Optional[str] = Field(None, max_length=255, description="Client's email address")
    start_time: datetime = Field(..., description="Booking start time")
    end_time: datetime = Field(..., description="Booking end time")
    space_type: SpaceType = Field(..., description="Type of space to book")
    equipment_requested: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Requested equipment")
    special_requirements: Optional[str] = Field(None, max_length=1000, description="Special requirements")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")
    people_count: int = Field(1, ge=1, le=50, description="Number of people")
    priority: int = Field(1, ge=1, le=5, description="Priority level (1=low, 5=high)")
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('start_time')
    def validate_start_time(cls, v):
        if v <= datetime.now():
            raise ValueError('Start time must be in the future')
        return v

class UpdateBookingRequest(BaseModel):
    """Request model for updating a booking."""
    client_name: Optional[str] = Field(None, min_length=2, max_length=200)
    client_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    client_email: Optional[str] = Field(None, max_length=255)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    space_type: Optional[SpaceType] = None
    equipment_requested: Optional[Dict[str, Any]] = None
    special_requirements: Optional[str] = Field(None, max_length=1000)
    notes: Optional[str] = Field(None, max_length=1000)
    people_count: Optional[int] = Field(None, ge=1, le=50)
    priority: Optional[int] = Field(None, ge=1, le=5)
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'start_time' in values and v and values['start_time'] and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v

class StateTransitionRequest(BaseModel):
    """Request model for state transitions."""
    target_state: BookingState = Field(..., description="Target state to transition to")
    reason: Optional[str] = Field(None, max_length=500, description="Reason for transition")

class CancelBookingRequest(BaseModel):
    """Request model for cancelling a booking."""
    reason: Optional[str] = Field(None, max_length=500, description="Reason for cancellation")

class BookingResponse(BaseModel):
    """Response model for booking data."""
    id: int
    booking_reference: str
    client_name: str
    client_phone: str
    client_email: Optional[str]
    start_time: datetime
    end_time: datetime
    duration_hours: float
    state: str
    space_type: str
    equipment_requested: Optional[Dict[str, Any]]
    special_requirements: Optional[str]
    people_count: int
    base_price: float
    equipment_price: float
    discount_amount: float
    total_price: float
    payment_status: str
    source: str
    notes: Optional[str]
    internal_notes: Optional[str]
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BookingSummaryResponse(BaseModel):
    """Response model for booking summary."""
    id: int
    booking_reference: str
    client_name: str
    start_time: datetime
    end_time: datetime
    state: str
    space_type: str
    total_price: float
    payment_status: str
    priority: int

class BookingListResponse(BaseModel):
    """Response model for booking list."""
    bookings: List[BookingSummaryResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str
    message: str
    code: str
    details: Optional[Dict[str, Any]] = None

# Dependency injection
async def get_booking_service() -> BookingDomainService:
    """Get booking domain service instance."""
    # This would be injected from dependency container
    # For now, return a mock instance
    from ...repositories.booking_repository import BookingRepository
    from ...repositories.employee_repository import EmployeeRepository
    
    # Mock repositories for now
    booking_repo = BookingRepository(None, None)
    employee_repo = EmployeeRepository(None, None)
    
    return BookingDomainService(booking_repo, None, None, None)

async def get_security_context(
    current_user: Employee = Depends(get_current_user)
) -> SecurityContext:
    """Get security context for current user."""
    return SecurityContext(
        employee_id=current_user.id,
        username=current_user.username,
        role=current_user.role.value,
        session_id="mock_session",
        ip_address="127.0.0.1",
        user_agent="mock_agent",
        permissions=[],
        mfa_verified=True
    )

async def get_current_user() -> Employee:
    """Get current authenticated user."""
    # This would implement proper authentication
    # For now, return a mock user
    from ...models.employee_enhanced import Employee, EmployeeRole, EmployeeStatus
    
    return Employee(
        id=1,
        username="admin",
        email="admin@example.com",
        password_hash="mock_hash",
        role=EmployeeRole.ADMIN,
        status=EmployeeStatus.ACTIVE,
        full_name="Admin User"
    )

# API Endpoints
@router.post(
    "/",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse}
    },
    summary="Create a new booking",
    description="Create a new booking with comprehensive validation and business rules"
)
async def create_booking(
    request: CreateBookingRequest,
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> BookingResponse:
    """
    Create a new booking with comprehensive validation.
    
    This endpoint:
    - Validates time slots are available
    - Ensures booking starts and ends at valid times
    - Normalizes phone numbers
    - Generates unique booking reference
    - Emits domain events
    """
    try:
        # Create command
        command = CreateBookingCommand(
            client_name=request.client_name,
            client_phone=request.client_phone,
            client_email=request.client_email,
            start_time=request.start_time,
            end_time=request.end_time,
            space_type=request.space_type.value,
            equipment_requested=request.equipment_requested,
            special_requirements=request.special_requirements,
            notes=request.notes
        )
        
        # Execute command
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        result = await booking_service.create_booking(command, context)
        
        if result.is_failure():
            error = result.error
            if hasattr(error, 'code'):
                if error.code == "TIME_SLOT_UNAVAILABLE":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail={
                            "error": "Time slot unavailable",
                            "message": error.message,
                            "code": error.code,
                            "details": error.details
                        }
                    )
                elif error.code == "VALIDATION_ERROR":
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Validation error",
                            "message": error.message,
                            "code": error.code,
                            "details": error.details
                        }
                    )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Booking creation failed",
                    "message": error.message,
                    "code": getattr(error, 'code', 'UNKNOWN_ERROR')
                }
            )
        
        booking = result.value
        return BookingResponse.from_orm(booking)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    responses={
        404: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    },
    summary="Get booking by ID",
    description="Retrieve a specific booking by its ID"
)
@cached(ttl=300, key_prefix="booking")
async def get_booking(
    booking_id: int = Path(..., description="Booking ID"),
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> BookingResponse:
    """Get a specific booking by ID."""
    try:
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        result = await booking_service.get_booking(booking_id, context)
        
        if result.is_failure():
            error = result.error
            if error.code == "BOOKING_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Booking not found",
                        "message": error.message,
                        "code": error.code
                    }
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to retrieve booking",
                    "message": error.message,
                    "code": error.code
                }
            )
        
        booking = result.value
        return BookingResponse.from_orm(booking)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.put(
    "/{booking_id}",
    response_model=BookingResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    },
    summary="Update booking",
    description="Update an existing booking"
)
@cache_invalidate("booking:*")
async def update_booking(
    booking_id: int = Path(..., description="Booking ID"),
    request: UpdateBookingRequest = ...,
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> BookingResponse:
    """Update an existing booking."""
    try:
        # Create command
        command = UpdateBookingCommand(
            booking_id=booking_id,
            client_name=request.client_name,
            client_phone=request.client_phone,
            client_email=request.client_email,
            start_time=request.start_time,
            end_time=request.end_time,
            space_type=request.space_type.value if request.space_type else None,
            equipment_requested=request.equipment_requested,
            special_requirements=request.special_requirements,
            notes=request.notes
        )
        
        # Execute command
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        result = await booking_service.update_booking(booking_id, command, context)
        
        if result.is_failure():
            error = result.error
            if error.code == "BOOKING_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Booking not found",
                        "message": error.message,
                        "code": error.code
                    }
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to update booking",
                    "message": error.message,
                    "code": error.code
                }
            )
        
        booking = result.value
        return BookingResponse.from_orm(booking)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.post(
    "/{booking_id}/state",
    response_model=BookingResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    },
    summary="Transition booking state",
    description="Transition booking to a new state with validation"
)
@cache_invalidate("booking:*")
async def transition_booking_state(
    booking_id: int = Path(..., description="Booking ID"),
    request: StateTransitionRequest = ...,
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> BookingResponse:
    """Transition booking to a new state."""
    try:
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        result = await booking_service.transition_state(
            booking_id, request.target_state, context, request.reason
        )
        
        if result.is_failure():
            error = result.error
            if error.code == "BOOKING_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Booking not found",
                        "message": error.message,
                        "code": error.code
                    }
                )
            elif error.code == "INVALID_STATE_TRANSITION":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Invalid state transition",
                        "message": error.message,
                        "code": error.code
                    }
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to transition state",
                    "message": error.message,
                    "code": error.code
                }
            )
        
        booking = result.value
        return BookingResponse.from_orm(booking)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.post(
    "/{booking_id}/cancel",
    response_model=BookingResponse,
    responses={
        404: {"model": ErrorResponse},
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    },
    summary="Cancel booking",
    description="Cancel a booking with proper cleanup and notifications"
)
@cache_invalidate("booking:*")
async def cancel_booking(
    booking_id: int = Path(..., description="Booking ID"),
    request: CancelBookingRequest = ...,
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> BookingResponse:
    """Cancel a booking."""
    try:
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        result = await booking_service.cancel_booking(booking_id, context, request.reason)
        
        if result.is_failure():
            error = result.error
            if error.code == "BOOKING_NOT_FOUND":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": "Booking not found",
                        "message": error.message,
                        "code": error.code
                    }
                )
            elif error.code == "CANCELLATION_NOT_ALLOWED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "Cancellation not allowed",
                        "message": error.message,
                        "code": error.code
                    }
                )
            
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to cancel booking",
                    "message": error.message,
                    "code": error.code
                }
            )
        
        booking = result.value
        return BookingResponse.from_orm(booking)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.get(
    "/",
    response_model=BookingListResponse,
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    },
    summary="Get bookings with filtering",
    description="Get list of bookings with advanced filtering and pagination"
)
@cached(ttl=300, key_prefix="bookings_list")
async def get_bookings(
    date: Optional[date] = Query(None, description="Filter by specific date"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    state: Optional[BookingState] = Query(None, description="Filter by booking state"),
    space_type: Optional[SpaceType] = Query(None, description="Filter by space type"),
    client_name: Optional[str] = Query(None, description="Filter by client name"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> BookingListResponse:
    """Get list of bookings with filtering and pagination."""
    try:
        # Build filters
        filters = {}
        if date:
            filters["date"] = date
        if start_date:
            filters["start_date"] = start_date
        if end_date:
            filters["end_date"] = end_date
        if state:
            filters["state"] = state
        if space_type:
            filters["space_type"] = space_type
        if client_name:
            filters["client_name"] = client_name
        if payment_status:
            filters["payment_status"] = payment_status
        
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get bookings
        result = await booking_service.get_bookings_for_date(
            date or datetime.now().date(),
            context,
            filters
        )
        
        if result.is_failure():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to retrieve bookings",
                    "message": result.error.message,
                    "code": result.error.code
                }
            )
        
        bookings = result.value
        
        # Apply pagination
        total = len(bookings)
        start_idx = offset
        end_idx = start_idx + page_size
        paginated_bookings = bookings[start_idx:end_idx]
        
        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size
        
        # Convert to response models
        booking_responses = [
            BookingSummaryResponse.from_orm(booking)
            for booking in paginated_bookings
        ]
        
        return BookingListResponse(
            bookings=booking_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

@router.get(
    "/analytics/summary",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse}
    },
    summary="Get booking analytics",
    description="Get comprehensive booking analytics and statistics"
)
@cached(ttl=600, key_prefix="booking_analytics")
async def get_booking_analytics(
    start_date: date = Query(..., description="Start date for analytics"),
    end_date: date = Query(..., description="End date for analytics"),
    group_by: Optional[str] = Query(None, description="Grouping field (date, space_type, state)"),
    booking_service: BookingDomainService = Depends(get_booking_service),
    security_context: SecurityContext = Depends(get_security_context)
) -> Dict[str, Any]:
    """Get booking analytics for a date range."""
    try:
        context = {
            "user_id": security_context.employee_id,
            "ip_address": security_context.ip_address,
            "user_agent": security_context.user_agent
        }
        
        result = await booking_service.get_booking_analytics(
            start_date, end_date, context, group_by
        )
        
        if result.is_failure():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "Failed to retrieve analytics",
                    "message": result.error.message,
                    "code": result.error.code
                }
            )
        
        return result.value
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred",
                "code": "INTERNAL_ERROR"
            }
        )

# Health check endpoint
@router.get(
    "/health",
    summary="Health check",
    description="Check if the booking service is healthy"
)
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "booking-api"}

# Error handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "code": "INTERNAL_ERROR"
        }
    )
