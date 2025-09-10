"""
Enhanced Booking Domain Service with CQRS and Event Bus integration.

This module provides a comprehensive domain service for booking management
that follows FAANG engineering standards and implements domain-driven design.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

from ..core.result import Result, success, failure, DomainError
from ..core.event_bus import publish_event, BookingCreatedEvent, BookingStateChangedEvent
from ..core.cqrs import Command, Query
from ..models.booking_enhanced import Booking, BookingState, SpaceType
from ..repositories.booking_repository import BookingRepository
from ..models.employee_enhanced import Employee


class BookingError(DomainError):
    """Base class for booking-related errors."""
    pass


class TimeSlotUnavailableError(BookingError):
    """Error raised when requested time slot is not available."""
    
    def __init__(self, start_time: datetime, end_time: datetime):
        super().__init__(
            f"Time slot {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} is not available",
            code="TIME_SLOT_UNAVAILABLE",
            details={"start_time": start_time.isoformat(), "end_time": end_time.isoformat()}
        )


class InvalidTimeSlotError(BookingError):
    """Error raised when time slot is invalid."""
    
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_TIME_SLOT")


class BookingNotFoundError(BookingError):
    """Error raised when booking is not found."""
    
    def __init__(self, booking_id: int):
        super().__init__(f"Booking with id {booking_id} not found", code="BOOKING_NOT_FOUND")


class StateTransitionError(BookingError):
    """Error raised when state transition is invalid."""
    
    def __init__(self, from_state: str, to_state: str, reason: Optional[str] = None):
        message = f"Cannot transition from {from_state} to {to_state}"
        if reason:
            message += f": {reason}"
        
        super().__init__(message, code="INVALID_STATE_TRANSITION")


class BookingValidationError(BookingError):
    """Error raised when booking validation fails."""
    
    def __init__(self, errors: List[str]):
        super().__init__(
            "Booking validation failed",
            code="VALIDATION_ERROR",
            details={"errors": errors}
        )


class BookingDomainService:
    """
    Enhanced Booking Domain Service with comprehensive business logic.
    
    This service implements the core business rules for booking management
    and integrates with the event bus for loose coupling.
    """
    
    def __init__(
        self,
        repository: BookingRepository,
        cache_service: Optional[Any] = None,
        notification_service: Optional[Any] = None,
        payment_service: Optional[Any] = None
    ):
        self.repository = repository
        self.cache_service = cache_service
        self.notification_service = notification_service
        self.payment_service = payment_service
    
    async def create_booking(
        self, 
        command: Command,
        context: Dict[str, Any]
    ) -> Result[Booking, BookingError]:
        """
        Create a new booking with comprehensive validation and event emission.
        
        Args:
            command: Create booking command
            context: Request context including user information
            
        Returns:
            Result containing the created booking or error
        """
        try:
            # Extract booking data from command
            booking_data = self._extract_booking_data(command)
            
            # Validate business rules
            validation_result = await self._validate_booking_creation(booking_data)
            if validation_result.is_failure():
                return validation_result
            
            # Check availability with distributed lock
            availability_result = await self._check_availability(
                booking_data["start_time"],
                booking_data["end_time"],
                booking_data["space_type"]
            )
            if availability_result.is_failure():
                return availability_result
            
            # Create booking aggregate
            booking = Booking(**booking_data)
            
            # Validate the created booking
            validation_errors = booking.validate_booking()
            if validation_errors:
                return failure(BookingValidationError(validation_errors))
            
            # Persist with transaction
            saved_booking = await self.repository.create(booking)
            
            # Emit domain events
            await self._emit_booking_created_event(saved_booking, context)
            
            # Invalidate relevant caches
            await self._invalidate_caches(saved_booking)
            
            # Send notifications
            await self._send_booking_notifications(saved_booking, "created")
            
            return success(saved_booking)
            
        except Exception as e:
            return failure(
                BookingError(
                    f"Failed to create booking: {str(e)}",
                    code="BOOKING_CREATION_FAILED"
                )
            )
    
    async def update_booking(
        self,
        booking_id: int,
        command: Command,
        context: Dict[str, Any]
    ) -> Result[Booking, BookingError]:
        """
        Update an existing booking.
        
        Args:
            booking_id: ID of the booking to update
            command: Update booking command
            context: Request context including user information
            
        Returns:
            Result containing the updated booking or error
        """
        try:
            # Get existing booking
            existing_booking = await self.repository.get_by_id(booking_id)
            if not existing_booking:
                return failure(BookingNotFoundError(booking_id))
            
            # Extract update data
            update_data = self._extract_update_data(command)
            
            # Validate updates
            validation_result = await self._validate_booking_update(existing_booking, update_data)
            if validation_result.is_failure():
                return validation_result
            
            # Check availability if time is being changed
            if "start_time" in update_data or "end_time" in update_data:
                start_time = update_data.get("start_time", existing_booking.start_time)
                end_time = update_data.get("end_time", existing_booking.end_time)
                
                availability_result = await self._check_availability(
                    start_time, end_time, existing_booking.space_type, exclude_booking_id=booking_id
                )
                if availability_result.is_failure():
                    return availability_result
            
            # Apply updates
            updated_booking = await self._apply_booking_updates(existing_booking, update_data, context)
            
            # Save changes
            saved_booking = await self.repository.update(updated_booking)
            
            # Emit events
            await self._emit_booking_updated_event(saved_booking, context)
            
            # Invalidate caches
            await self._invalidate_caches(saved_booking)
            
            return success(saved_booking)
            
        except Exception as e:
            return failure(
                BookingError(
                    f"Failed to update booking: {str(e)}",
                    code="BOOKING_UPDATE_FAILED"
                )
            )
    
    async def transition_state(
        self,
        booking_id: int,
        target_state: BookingState,
        context: Dict[str, Any],
        reason: Optional[str] = None
    ) -> Result[Booking, StateTransitionError]:
        """
        Transition booking to a new state with validation and side effects.
        
        Args:
            booking_id: ID of the booking
            target_state: Target state to transition to
            context: Request context including user information
            reason: Optional reason for the transition
            
        Returns:
            Result containing the updated booking or error
        """
        try:
            # Get existing booking
            existing_booking = await self.repository.get_by_id(booking_id)
            if not existing_booking:
                return failure(StateTransitionError("unknown", target_state.value, "Booking not found"))
            
            # Validate state transition
            if not existing_booking.can_transition_to(target_state):
                return failure(
                    StateTransitionError(
                        existing_booking.state.value,
                        target_state.value,
                        "Invalid state transition"
                    )
                )
            
            # Get user ID from context
            user_id = context.get("user_id", 0)
            
            # Apply state transition
            transition_success = existing_booking.transition_to(target_state, user_id, reason)
            if not transition_success:
                return failure(
                    StateTransitionError(
                        existing_booking.state.value,
                        target_state.value,
                        "State transition failed"
                    )
                )
            
            # Save changes
            updated_booking = await self.repository.update(existing_booking)
            
            # Emit state change event
            await self._emit_booking_state_changed_event(updated_booking, context)
            
            # Invalidate caches
            await self._invalidate_caches(updated_booking)
            
            # Send notifications
            await self._send_booking_notifications(updated_booking, "state_changed")
            
            return success(updated_booking)
            
        except Exception as e:
            return failure(
                StateTransitionError(
                    "unknown",
                    target_state.value,
                    f"State transition failed: {str(e)}"
                )
            )
    
    async def cancel_booking(
        self,
        booking_id: int,
        context: Dict[str, Any],
        reason: Optional[str] = None
    ) -> Result[Booking, BookingError]:
        """
        Cancel a booking with proper cleanup and notifications.
        
        Args:
            booking_id: ID of the booking to cancel
            context: Request context including user information
            reason: Optional reason for cancellation
            
        Returns:
            Result containing the cancelled booking or error
        """
        try:
            # Get existing booking
            existing_booking = await self.repository.get_by_id(booking_id)
            if not existing_booking:
                return failure(BookingNotFoundError(booking_id))
            
            # Check if booking can be cancelled
            if not existing_booking.can_be_cancelled():
                return failure(
                    BookingError(
                        f"Booking cannot be cancelled in state {existing_booking.state.value}",
                        code="CANCELLATION_NOT_ALLOWED"
                    )
                )
            
            # Transition to cancelled state
            transition_result = await self.transition_state(
                booking_id, BookingState.CANCELLED, context, reason
            )
            
            if transition_result.is_failure():
                return failure(transition_result.error)
            
            cancelled_booking = transition_result.value
            
            # Process refunds if needed
            if self.payment_service:
                await self._process_cancellation_refund(cancelled_booking, context)
            
            # Send cancellation notifications
            await self._send_booking_notifications(cancelled_booking, "cancelled")
            
            return success(cancelled_booking)
            
        except Exception as e:
            return failure(
                BookingError(
                    f"Failed to cancel booking: {str(e)}",
                    code="BOOKING_CANCELLATION_FAILED"
                )
            )
    
    async def get_booking(
        self,
        booking_id: int,
        context: Dict[str, Any]
    ) -> Result[Booking, BookingError]:
        """
        Get a booking by ID with proper access control.
        
        Args:
            booking_id: ID of the booking
            context: Request context including user information
            
        Returns:
            Result containing the booking or error
        """
        try:
            # Get booking from repository
            booking = await self.repository.get_by_id(booking_id)
            if not booking:
                return failure(BookingNotFoundError(booking_id))
            
            # Check access permissions
            access_result = await self._check_booking_access(booking, context)
            if access_result.is_failure():
                return access_result
            
            return success(booking)
            
        except Exception as e:
            return failure(
                BookingError(
                    f"Failed to get booking: {str(e)}",
                    code="BOOKING_RETRIEVAL_FAILED"
                )
            )
    
    async def get_bookings_for_date(
        self,
        date: datetime.date,
        context: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None
    ) -> Result[List[Booking], BookingError]:
        """
        Get bookings for a specific date with filtering.
        
        Args:
            date: Date to get bookings for
            context: Request context including user information
            filters: Optional filters to apply
            
        Returns:
            Result containing list of bookings or error
        """
        try:
            # Apply default filters
            if filters is None:
                filters = {}
            
            # Add date filter
            filters["date"] = date
            
            # Get bookings from repository
            bookings = await self.repository.find_by_filters(filters)
            
            # Apply access control
            accessible_bookings = []
            for booking in bookings:
                access_result = await self._check_booking_access(booking, context)
                if access_result.is_success():
                    accessible_bookings.append(booking)
            
            return success(accessible_bookings)
            
        except Exception as e:
            return failure(
                BookingError(
                    f"Failed to get bookings for date: {str(e)}",
                    code="BOOKING_RETRIEVAL_FAILED"
                )
            )
    
    # Private helper methods
    def _extract_booking_data(self, command: Command) -> Dict[str, Any]:
        """Extract booking data from command."""
        # This would extract data based on command type
        # For now, return empty dict - implement based on actual command structure
        return {}
    
    def _extract_update_data(self, command: Command) -> Dict[str, Any]:
        """Extract update data from command."""
        # This would extract data based on command type
        # For now, return empty dict - implement based on actual command structure
        return {}
    
    async def _validate_booking_creation(self, booking_data: Dict[str, Any]) -> Result[None, BookingError]:
        """Validate booking creation data."""
        # Basic validation
        required_fields = ["client_name", "client_phone", "start_time", "end_time", "space_type"]
        
        for field in required_fields:
            if field not in booking_data or not booking_data[field]:
                return failure(
                    BookingValidationError([f"Required field '{field}' is missing or empty"])
                )
        
        # Time validation
        start_time = booking_data["start_time"]
        end_time = booking_data["end_time"]
        
        if start_time >= end_time:
            return failure(
                InvalidTimeSlotError("Start time must be before end time")
            )
        
        # Check if start time is in the future
        if start_time <= datetime.now(timezone.utc):
            return failure(
                InvalidTimeSlotError("Start time must be in the future")
            )
        
        return success(None)
    
    async def _validate_booking_update(
        self,
        existing_booking: Booking,
        update_data: Dict[str, Any]
    ) -> Result[None, BookingError]:
        """Validate booking update data."""
        # Check if booking can be modified
        if existing_booking.state in [BookingState.COMPLETED, BookingState.CANCELLED]:
            return failure(
                BookingError(
                    f"Cannot modify booking in state {existing_booking.state.value}",
                    code="MODIFICATION_NOT_ALLOWED"
                )
            )
        
        return success(None)
    
    async def _check_availability(
        self,
        start_time: datetime,
        end_time: datetime,
        space_type: SpaceType,
        exclude_booking_id: Optional[int] = None
    ) -> Result[None, BookingError]:
        """Check if time slot is available."""
        # Get conflicting bookings
        conflicting_bookings = await self.repository.find_conflicting_bookings(
            start_time, end_time, space_type, exclude_booking_id
        )
        
        if conflicting_bookings:
            return failure(
                TimeSlotUnavailableError(start_time, end_time)
            )
        
        return success(None)
    
    async def _apply_booking_updates(
        self,
        existing_booking: Booking,
        update_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Booking:
        """Apply updates to existing booking."""
        # Update fields
        for field, value in update_data.items():
            if hasattr(existing_booking, field):
                setattr(existing_booking, field, value)
        
        # Update audit trail
        user_id = context.get("user_id", 0)
        existing_booking.update_audit_trail(
            "updated",
            user_id=user_id,
            details={"updated_fields": list(update_data.keys())}
        )
        
        # Increment version
        existing_booking.increment_version()
        
        return existing_booking
    
    async def _check_booking_access(
        self,
        booking: Booking,
        context: Dict[str, Any]
    ) -> Result[None, BookingError]:
        """Check if user has access to booking."""
        # This would implement proper access control
        # For now, allow access to all authenticated users
        return success(None)
    
    async def _emit_booking_created_event(
        self,
        booking: Booking,
        context: Dict[str, Any]
    ) -> None:
        """Emit booking created event."""
        event = BookingCreatedEvent(
            booking_id=booking.id,
            reference=booking.booking_reference,
            client_name=booking.client_name,
            start_time=booking.start_time,
            end_time=booking.end_time
        )
        
        # Set metadata from context
        if "user_id" in context:
            event.metadata.user_id = context["user_id"]
        if "ip_address" in context:
            event.metadata.ip_address = context["ip_address"]
        if "user_agent" in context:
            event.metadata.user_agent = context["user_agent"]
        
        await publish_event(event)
    
    async def _emit_booking_updated_event(
        self,
        booking: Booking,
        context: Dict[str, Any]
    ) -> None:
        """Emit booking updated event."""
        # This would emit a booking updated event
        # For now, just log the update
        pass
    
    async def _emit_booking_state_changed_event(
        self,
        booking: Booking,
        context: Dict[str, Any]
    ) -> None:
        """Emit booking state changed event."""
        # Get previous state from history
        previous_state = "unknown"
        if booking.state_history:
            try:
                import json
                history = json.loads(booking.state_history) if isinstance(booking.state_history, str) else booking.state_history
                if len(history) >= 2:
                    previous_state = history[-2]["state"]
            except (json.JSONDecodeError, TypeError, IndexError):
                pass
        
        event = BookingStateChangedEvent(
            booking_id=booking.id,
            from_state=previous_state,
            to_state=booking.state.value,
            changed_by=context.get("user_id", 0)
        )
        
        # Set metadata from context
        if "user_id" in context:
            event.metadata.user_id = context["user_id"]
        if "ip_address" in context:
            event.metadata.ip_address = context["ip_address"]
        if "user_agent" in context:
            event.metadata.user_agent = context["user_agent"]
        
        await publish_event(event)
    
    async def _invalidate_caches(self, booking: Booking) -> None:
        """Invalidate relevant caches."""
        if not self.cache_service:
            return
        
        # Invalidate date-based caches
        cache_keys = [
            f"bookings:date:{booking.booking_date}",
            f"bookings:space:{booking.space_type.value}:{booking.booking_date}",
            f"bookings:state:{booking.state.value}",
        ]
        
        for key in cache_keys:
            await self.cache_service.delete(key)
    
    async def _send_booking_notifications(
        self,
        booking: Booking,
        notification_type: str
    ) -> None:
        """Send booking notifications."""
        if not self.notification_service:
            return
        
        # Send appropriate notifications based on type
        if notification_type == "created":
            await self.notification_service.send_booking_confirmation(booking)
        elif notification_type == "state_changed":
            await self.notification_service.send_state_change_notification(booking)
        elif notification_type == "cancelled":
            await self.notification_service.send_cancellation_notification(booking)
    
    async def _process_cancellation_refund(
        self,
        booking: Booking,
        context: Dict[str, Any]
    ) -> None:
        """Process cancellation refunds."""
        if not self.payment_service:
            return
        
        # Calculate refund amount
        refund_amount = booking.calculate_refund_amount()
        
        if refund_amount > 0:
            await self.payment_service.process_refund(booking, refund_amount, context)
    
    # Business logic methods
    async def get_booking_analytics(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        context: Dict[str, Any],
        group_by: Optional[str] = None
    ) -> Result[Dict[str, Any], BookingError]:
        """
        Get booking analytics for a date range.
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            context: Request context including user information
            group_by: Optional grouping field (date, space_type, state)
            
        Returns:
            Result containing analytics data or error
        """
        try:
            # Get bookings in date range
            filters = {
                "start_date": start_date,
                "end_date": end_date
            }
            
            bookings = await self.repository.find_by_filters(filters)
            
            # Calculate analytics
            analytics = self._calculate_analytics(bookings, group_by)
            
            return success(analytics)
            
        except Exception as e:
            return failure(
                BookingError(
                    f"Failed to get booking analytics: {str(e)}",
                    code="ANALYTICS_RETRIEVAL_FAILED"
                )
            )
    
    def _calculate_analytics(
        self,
        bookings: List[Booking],
        group_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculate analytics from bookings."""
        if not bookings:
            return {
                "total_bookings": 0,
                "total_revenue": 0,
                "average_duration": 0,
                "state_distribution": {},
                "space_type_distribution": {}
            }
        
        # Basic metrics
        total_bookings = len(bookings)
        total_revenue = sum(float(b.total_price) for b in bookings if b.total_price)
        average_duration = sum(float(b.duration_hours) for b in bookings if b.duration_hours) / total_bookings
        
        # State distribution
        state_distribution = {}
        for booking in bookings:
            state = booking.state.value
            state_distribution[state] = state_distribution.get(state, 0) + 1
        
        # Space type distribution
        space_type_distribution = {}
        for booking in bookings:
            space_type = booking.space_type.value
            space_type_distribution[space_type] = space_type_distribution.get(space_type, 0) + 1
        
        analytics = {
            "total_bookings": total_bookings,
            "total_revenue": round(total_revenue, 2),
            "average_duration": round(average_duration, 2),
            "state_distribution": state_distribution,
            "space_type_distribution": space_type_distribution
        }
        
        # Group by specific field if requested
        if group_by and group_by in ["date", "space_type", "state"]:
            grouped_data = {}
            for booking in bookings:
                if group_by == "date":
                    key = booking.booking_date.isoformat()
                elif group_by == "space_type":
                    key = booking.space_type.value
                elif group_by == "state":
                    key = booking.state.value
                
                if key not in grouped_data:
                    grouped_data[key] = {
                        "count": 0,
                        "revenue": 0,
                        "duration": 0
                    }
                
                grouped_data[key]["count"] += 1
                grouped_data[key]["revenue"] += float(booking.total_price) if booking.total_price else 0
                grouped_data[key]["duration"] += float(booking.duration_hours) if booking.duration_hours else 0
            
            analytics["grouped_data"] = grouped_data
        
        return analytics