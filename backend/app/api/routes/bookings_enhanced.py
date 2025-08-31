from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging

from ...core.database import get_db
from ...models.booking_enhanced import Booking, BookingState, BookingSource
from ...repositories.booking_repository import BookingRepository
from ...core.cqrs import (
    BookingCommandHandler, BookingQueryHandler,
    CreateBookingCommand, UpdateBookingStateCommand, DeleteBookingCommand,
    GetBookingsQuery, GetBookingByIdQuery, GetBookingByReferenceQuery,
    BookingDTO
)
from ...services.booking_domain_service import BookingDomainService
from ...core.event_bus import event_bus
from ...core.validation import BookingValidator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["bookings"])

# Pydantic models for API
class BookingCreate(BaseModel):
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    booking_date: str
    start_time: str
    end_time: str
    space_type: str
    duration_hours: int
    base_price: float
    total_price: float
    special_requirements: Optional[str] = None
    source: str = "website"

class BookingUpdateState(BaseModel):
    new_state: BookingState
    notes: Optional[str] = None

class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    booking_date: str
    start_time: str
    end_time: str
    state: BookingState
    space_type: str
    duration_hours: int
    base_price: float
    total_price: float
    special_requirements: Optional[str] = None
    source: str
    created_at: str
    updated_at: str
    state_history: List[dict]

class BookingListResponse(BaseModel):
    bookings: List[BookingResponse]
    total: int

# Helper function to convert Booking DTO to response
def booking_dto_to_response(booking_dto: BookingDTO) -> BookingResponse:
    # In a real implementation, we would get the full booking entity to include all fields
    # For now, we'll create a minimal response
    return BookingResponse(
        id=booking_dto.id,
        booking_reference=booking_dto.booking_reference,
        client_name=booking_dto.client_name,
        client_phone=booking_dto.client_phone,
        booking_date=booking_dto.booking_date,
        start_time=booking_dto.start_time,
        end_time=booking_dto.end_time,
        state=booking_dto.state,
        space_type=booking_dto.space_type,
        duration_hours=booking_dto.duration_hours,
        base_price=0.0,  # Not in DTO
        total_price=booking_dto.total_price,
        special_requirements=None,  # Not in DTO
        source="website",  # Not in DTO
        created_at=booking_dto.created_at,
        updated_at=booking_dto.created_at,  # Not in DTO
        state_history=[]  # Not in DTO
    )

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db)
):
    """Create a new booking using CQRS pattern"""
    # Validate input
    validator = BookingValidator()
    validation_result = validator.validate_booking_data(booking_data.dict())
    
    if not validation_result.is_valid():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "validation_error",
                "message": "Invalid booking data",
                "details": [error.__dict__ for error in validation_result.get_errors()]
            }
        )
    
    try:
        # Create command
        command = CreateBookingCommand(
            client_name=booking_data.client_name,
            client_phone=booking_data.client_phone,
            client_phone_normalized=booking_data.client_phone,  # In real implementation, normalize this
            client_email=booking_data.client_email,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            space_type=booking_data.space_type,
            duration_hours=booking_data.duration_hours,
            base_price=booking_data.base_price,
            total_price=booking_data.total_price,
            special_requirements=booking_data.special_requirements,
            source=booking_data.source
        )
        
        # Execute command
        booking_repo = BookingRepository(db)
        command_handler = BookingCommandHandler(booking_repo)
        result = await command_handler.handle(command)
        
        if not result.success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error
            )
        
        # For now, return a simple response
        # In a real implementation, we would return the created booking
        return BookingResponse(
            id=1,  # Placeholder
            booking_reference="REF-20230101-0001",  # Placeholder
            client_name=booking_data.client_name,
            client_phone=booking_data.client_phone,
            client_email=booking_data.client_email,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            state=BookingState.PENDING,
            space_type=booking_data.space_type,
            duration_hours=booking_data.duration_hours,
            base_price=booking_data.base_price,
            total_price=booking_data.total_price,
            special_requirements=booking_data.special_requirements,
            source=booking_data.source,
            created_at="2023-01-01T00:00:00Z",  # Placeholder
            updated_at="2023-01-01T00:00:00Z",  # Placeholder
            state_history=[]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )

@router.get("/", response_model=BookingListResponse)
async def list_bookings(
    date: Optional[str] = None,
    state: Optional[BookingState] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List bookings using CQRS pattern"""
    try:
        # Create query
        query = GetBookingsQuery(
            date=date,
            state=state,
            limit=limit,
            offset=skip
        )
        
        # Execute query
        booking_repo = BookingRepository(db)
        query_handler = BookingQueryHandler(booking_repo)
        booking_dtos = await query_handler.handle(query)
        
        # Convert to responses
        booking_responses = [booking_dto_to_response(dto) for dto in booking_dtos]
        
        return BookingListResponse(
            bookings=booking_responses,
            total=len(booking_responses)
        )
        
    except Exception as e:
        logger.error(f"Error listing bookings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list bookings"
        )

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Get booking by ID using CQRS pattern"""
    try:
        # Create query
        query = GetBookingByIdQuery(booking_id=booking_id)
        
        # Execute query
        booking_repo = BookingRepository(db)
        query_handler = BookingQueryHandler(booking_repo)
        booking_dto = await query_handler.handle(query)
        
        if not booking_dto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return booking_dto_to_response(booking_dto)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get booking"
        )

@router.patch("/{booking_id}/state", response_model=BookingResponse)
async def update_booking_state(
    booking_id: int,
    state_data: BookingUpdateState,
    db: Session = Depends(get_db)
):
    """Update booking state using domain service"""
    try:
        # Use domain service for state transition
        booking_service = BookingDomainService(db, event_bus)
        result = await booking_service.transition_state(
            booking_id=booking_id,
            target_state=state_data.new_state,
            notes=state_data.notes
        )
        
        if result.is_failure():
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.error
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.error
                )
        
        # Convert booking to response
        booking = result.value
        return BookingResponse(
            id=booking.id,
            booking_reference=booking.booking_reference,
            client_name=booking.client_name,
            client_phone=booking.client_phone,
            client_email=booking.client_email,
            booking_date=booking.booking_date.isoformat() if booking.booking_date else None,
            start_time=booking.start_time.isoformat() if booking.start_time else None,
            end_time=booking.end_time.isoformat() if booking.end_time else None,
            state=booking.state,
            space_type=booking.space_type,
            duration_hours=booking.duration_hours,
            base_price=float(booking.base_price) if booking.base_price else 0.0,
            total_price=float(booking.total_price) if booking.total_price else 0.0,
            special_requirements=booking.special_requirements,
            source=booking.source.value if booking.source else "website",
            created_at=booking.created_at.isoformat() if booking.created_at else None,
            updated_at=booking.updated_at.isoformat() if booking.updated_at else None,
            state_history=booking.state_history or []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating booking state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update booking state"
        )

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Delete booking using CQRS pattern"""
    try:
        # Create command
        command = DeleteBookingCommand(
            booking_id=booking_id,
            employee_id=1  # Placeholder - in real implementation, get from auth
        )
        
        # Execute command
        booking_repo = BookingRepository(db)
        command_handler = BookingCommandHandler(booking_repo)
        result = await command_handler.handle(command)
        
        if not result.success:
            if "not found" in result.error.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.error
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=result.error
                )
        
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete booking"
        )