from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
import logging
from .base_domain_service import BaseDomainService, Result
from ..models.booking_enhanced import Booking, BookingState
from ..models.domain_event import DomainEvent
from ..core.event_bus import EventBus, create_event

logger = logging.getLogger(__name__)

class BookingDomainService(BaseDomainService[Booking, None]):
    """Domain service for booking operations with state machine implementation"""
    
    def __init__(self, db: Session, event_bus: EventBus):
        super().__init__(db, event_bus)
    
    def _is_valid_transition(self, from_state: BookingState, to_state: BookingState) -> bool:
        """Validate if a state transition is allowed"""
        valid_transitions = {
            BookingState.DRAFT: [BookingState.PENDING, BookingState.CANCELLED],
            BookingState.PENDING: [BookingState.CONFIRMED, BookingState.CANCELLED],
            BookingState.CONFIRMED: [BookingState.IN_PROGRESS, BookingState.CANCELLED],
            BookingState.IN_PROGRESS: [BookingState.COMPLETED, BookingState.NO_SHOW, BookingState.CANCELLED],
            BookingState.COMPLETED: [],
            BookingState.CANCELLED: [BookingState.PENDING],  # Allow re-activation
            BookingState.NO_SHOW: [BookingState.PENDING],  # Allow re-activation
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    async def transition_state(
        self, 
        booking_id: int, 
        target_state: BookingState, 
        employee_id: int = None,
        notes: str = None
    ) -> Result[Booking]:
        """Transition a booking to a new state"""
        try:
            # Retrieve booking
            booking = self.db.query(Booking).filter(Booking.id == booking_id).first()
            if not booking:
                return Result.failure(f"Booking with id {booking_id} not found")
            
            # Validate transition
            if not self._is_valid_transition(booking.state, target_state):
                return Result.failure(
                    f"Invalid state transition from {booking.state.value} to {target_state.value}"
                )
            
            # Store previous state
            previous_state = booking.state
            
            # Update booking state
            booking.state = target_state
            
            # Add to state history
            state_history_entry = {
                "from_state": previous_state.value,
                "to_state": target_state.value,
                "timestamp": datetime.now().isoformat(),
                "employee_id": employee_id,
                "notes": notes
            }
            
            if booking.state_history is None:
                booking.state_history = []
            booking.state_history.append(state_history_entry)
            
            # Update in database
            self.db.add(booking)
            self._commit_transaction()
            self.db.refresh(booking)
            
            # Create and publish event
            event = create_event(
                event_type="booking_state_changed",
                payload={
                    "booking_id": booking.id,
                    "booking_reference": booking.booking_reference,
                    "from_state": previous_state.value,
                    "to_state": target_state.value,
                    "employee_id": employee_id
                }
            )
            await self._publish_event(event)
            
            self.logger.info(
                f"Booking {booking.id} state changed from {previous_state.value} to {target_state.value}"
            )
            
            return Result.success(booking)
            
        except Exception as e:
            self._rollback_transaction()
            error_msg = f"Failed to transition booking state: {str(e)}"
            self.logger.error(error_msg)
            return Result.failure(error_msg)
    
    def get_bookings_by_state(self, state: BookingState) -> Result[List[Booking]]:
        """Get all bookings with a specific state"""
        try:
            bookings = self.db.query(Booking).filter(Booking.state == state).all()
            return Result.success(bookings)
        except Exception as e:
            error_msg = f"Failed to retrieve bookings by state: {str(e)}"
            self.logger.error(error_msg)
            return Result.failure(error_msg)
    
    def get_bookings_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        state: BookingState = None
    ) -> Result[List[Booking]]:
        """Get bookings within a date range"""
        try:
            query = self.db.query(Booking).filter(
                and_(
                    Booking.booking_date >= start_date,
                    Booking.booking_date <= end_date
                )
            )
            
            if state:
                query = query.filter(Booking.state == state)
            
            bookings = query.all()
            return Result.success(bookings)
        except Exception as e:
            error_msg = f"Failed to retrieve bookings by date range: {str(e)}"
            self.logger.error(error_msg)
            return Result.failure(error_msg)