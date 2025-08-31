from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Any, Dict, List, Optional
from dataclasses import dataclass
import logging
from ..repositories.booking_repository import BookingRepository
from ..models.booking_enhanced import Booking, BookingState

logger = logging.getLogger(__name__)

# Command and Query type variables
C = TypeVar('C')  # Command type
Q = TypeVar('Q')  # Query type
R = TypeVar('R')  # Result type

@dataclass
class Command(ABC):
    """Base command class"""
    pass

@dataclass
class Query(ABC):
    """Base query class"""
    pass

@dataclass
class CommandResult:
    """Result of command execution"""
    success: bool
    data: Any = None
    error: str = None

class CommandHandler(ABC, Generic[C]):
    """Base command handler"""
    
    @abstractmethod
    async def handle(self, command: C) -> CommandResult:
        pass

class QueryHandler(ABC, Generic[Q, R]):
    """Base query handler"""
    
    @abstractmethod
    async def handle(self, query: Q) -> R:
        pass

# Specific commands
@dataclass
class CreateBookingCommand(Command):
    """Command to create a new booking"""
    client_name: str
    client_phone: str
    client_phone_normalized: str
    client_email: Optional[str]
    booking_date: str
    start_time: str
    end_time: str
    space_type: str
    duration_hours: int
    base_price: float
    total_price: float
    employee_id: Optional[int] = None
    special_requirements: Optional[str] = None
    source: str = "website"

@dataclass
class UpdateBookingStateCommand(Command):
    """Command to update booking state"""
    booking_id: int
    new_state: BookingState
    employee_id: Optional[int] = None
    notes: Optional[str] = None

@dataclass
class DeleteBookingCommand(Command):
    """Command to delete a booking"""
    booking_id: int
    employee_id: int

# Specific queries
@dataclass
class GetBookingsQuery(Query):
    """Query to get bookings"""
    date: Optional[str] = None
    state: Optional[BookingState] = None
    employee_id: Optional[int] = None
    limit: int = 100
    offset: int = 0

@dataclass
class GetBookingByIdQuery(Query):
    """Query to get booking by ID"""
    booking_id: int

@dataclass
class GetBookingByReferenceQuery(Query):
    """Query to get booking by reference"""
    reference: str

# Data Transfer Objects
@dataclass
class BookingDTO:
    """Data Transfer Object for booking"""
    id: int
    booking_reference: str
    client_name: str
    client_phone: str
    booking_date: str
    start_time: str
    end_time: str
    state: BookingState
    total_price: float
    space_type: str
    duration_hours: int
    created_at: str
    
    @classmethod
    def from_entity(cls, booking: Booking) -> 'BookingDTO':
        """Create DTO from booking entity"""
        return cls(
            id=booking.id,
            booking_reference=booking.booking_reference,
            client_name=booking.client_name,
            client_phone=booking.client_phone,
            booking_date=booking.booking_date.isoformat() if booking.booking_date else None,
            start_time=booking.start_time.isoformat() if booking.start_time else None,
            end_time=booking.end_time.isoformat() if booking.end_time else None,
            state=booking.state,
            total_price=float(booking.total_price) if booking.total_price else 0.0,
            space_type=booking.space_type,
            duration_hours=booking.duration_hours,
            created_at=booking.created_at.isoformat() if booking.created_at else None
        )

class BookingCommandHandler(CommandHandler[Command]):
    """Command handler for booking operations"""
    
    def __init__(self, booking_repository: BookingRepository):
        self.booking_repository = booking_repository
    
    async def handle(self, command: Command) -> CommandResult:
        """Handle booking commands"""
        try:
            if isinstance(command, CreateBookingCommand):
                return await self._handle_create_booking(command)
            elif isinstance(command, UpdateBookingStateCommand):
                return await self._handle_update_booking_state(command)
            elif isinstance(command, DeleteBookingCommand):
                return await self._handle_delete_booking(command)
            else:
                return CommandResult(
                    success=False,
                    error=f"Unknown command type: {type(command)}"
                )
        except Exception as e:
            logger.error(f"Error handling command: {e}")
            return CommandResult(
                success=False,
                error=str(e)
            )
    
    async def _handle_create_booking(self, command: CreateBookingCommand) -> CommandResult:
        """Handle create booking command"""
        # In a real implementation, we would create the booking entity
        # and save it to the database
        logger.info(f"Creating booking for {command.client_name}")
        return CommandResult(success=True, data={"message": "Booking created"})
    
    async def _handle_update_booking_state(self, command: UpdateBookingStateCommand) -> CommandResult:
        """Handle update booking state command"""
        # In a real implementation, we would update the booking state
        logger.info(f"Updating booking {command.booking_id} state to {command.new_state}")
        return CommandResult(success=True, data={"message": "Booking state updated"})
    
    async def _handle_delete_booking(self, command: DeleteBookingCommand) -> CommandResult:
        """Handle delete booking command"""
        # In a real implementation, we would delete the booking
        logger.info(f"Deleting booking {command.booking_id}")
        return CommandResult(success=True, data={"message": "Booking deleted"})

class BookingQueryHandler(QueryHandler[Query, Any]):
    """Query handler for booking operations"""
    
    def __init__(self, booking_repository: BookingRepository):
        self.booking_repository = booking_repository
    
    async def handle(self, query: Query) -> Any:
        """Handle booking queries"""
        try:
            if isinstance(query, GetBookingsQuery):
                return await self._handle_get_bookings(query)
            elif isinstance(query, GetBookingByIdQuery):
                return await self._handle_get_booking_by_id(query)
            elif isinstance(query, GetBookingByReferenceQuery):
                return await self._handle_get_booking_by_reference(query)
            else:
                raise ValueError(f"Unknown query type: {type(query)}")
        except Exception as e:
            logger.error(f"Error handling query: {e}")
            raise
    
    async def _handle_get_bookings(self, query: GetBookingsQuery) -> List[BookingDTO]:
        """Handle get bookings query"""
        # In a real implementation, we would query the database
        logger.info("Getting bookings")
        # Return empty list for now
        return []
    
    async def _handle_get_booking_by_id(self, query: GetBookingByIdQuery) -> Optional[BookingDTO]:
        """Handle get booking by ID query"""
        booking = self.booking_repository.get_by_id(query.booking_id)
        if booking:
            return BookingDTO.from_entity(booking)
        return None
    
    async def _handle_get_booking_by_reference(self, query: GetBookingByReferenceQuery) -> Optional[BookingDTO]:
        """Handle get booking by reference query"""
        # In a real implementation, we would query the database
        logger.info(f"Getting booking by reference: {query.reference}")
        return None