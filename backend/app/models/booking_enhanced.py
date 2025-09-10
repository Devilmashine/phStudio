"""
Enhanced Booking model with state machine and comprehensive features.

This module provides a production-grade booking model that includes:
- State machine for booking lifecycle
- Comprehensive validation
- Equipment and pricing management
- Audit trail and history tracking
- Performance optimization features
"""

from datetime import datetime, timezone, timedelta, date
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date, Text, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint, Numeric
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as SAEnum, JSON
from sqlalchemy.sql import func

from .base_enhanced import BaseEnhanced


class BookingState(str, PyEnum):
    """Booking states with lifecycle management."""
    DRAFT = "draft"              # Initial draft state
    PENDING = "pending"          # Awaiting confirmation
    CONFIRMED = "confirmed"      # Confirmed and scheduled
    IN_PROGRESS = "in_progress"  # Currently being processed
    COMPLETED = "completed"      # Successfully completed
    CANCELLED = "cancelled"      # Cancelled by client or staff
    NO_SHOW = "no_show"         # Client didn't show up
    RESCHEDULED = "rescheduled"  # Rescheduled to different time


class PaymentStatus(str, PyEnum):
    """Payment status tracking."""
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    FAILED = "failed"


class BookingSource(str, PyEnum):
    """Source of the booking."""
    WEBSITE = "website"
    PHONE = "phone"
    WALK_IN = "walk_in"
    EMAIL = "email"
    REFERRAL = "referral"
    SOCIAL_MEDIA = "social_media"


class SpaceType(str, PyEnum):
    """Available space types."""
    STUDIO_A = "studio_a"
    STUDIO_B = "studio_b"
    STUDIO_C = "studio_c"
    OUTDOOR = "outdoor"
    MEETING_ROOM = "meeting_room"
    DRESSING_ROOM = "dressing_room"


class Booking(BaseEnhanced):
    """
    Enhanced Booking model with comprehensive features.
    
    This model implements a state machine for booking lifecycle management
    and provides enterprise-grade booking capabilities.
    """
    
    __tablename__ = "bookings"
    
    # Booking identification
    booking_reference: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique booking reference (e.g., REF-20240101-0001)"
    )
    
    # Time management
    booking_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )
    
    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    duration_hours: Mapped[float] = mapped_column(
        Numeric(4, 2),
        nullable=False,
        comment="Duration in hours (cached for performance)"
    )
    
    # State management
    state: Mapped[BookingState] = mapped_column(
        SAEnum(BookingState),
        nullable=False,
        default=BookingState.PENDING,
        index=True
    )
    
    state_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(
        Text,  # JSON array stored as text
        nullable=True,
        comment="Complete state transition history"
    )
    
    # Client information
    client_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )
    
    client_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )
    
    client_phone_normalized: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        index=True,
        comment="E.164 normalized phone number"
    )
    
    client_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )
    
    # Booking details
    space_type: Mapped[SpaceType] = mapped_column(
        SAEnum(SpaceType),
        nullable=False,
        index=True
    )
    
    equipment_requested: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        Text,  # JSON stored as text
        nullable=True,
        comment="Requested equipment and accessories"
    )
    
    special_requirements: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    people_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False
    )
    
    # Pricing
    base_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Base price for the space and time"
    )
    
    equipment_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Additional equipment costs"
    )
    
    discount_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        default=0,
        nullable=False,
        comment="Discount amount applied"
    )
    
    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Total price after all adjustments"
    )
    
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SAEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True
    )
    
    # Metadata
    source: Mapped[BookingSource] = mapped_column(
        SAEnum(BookingSource),
        default=BookingSource.WEBSITE,
        nullable=False,
        index=True
    )
    
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Client-visible notes"
    )
    
    internal_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Staff-only notes"
    )
    
    tags: Mapped[Optional[List[str]]] = mapped_column(
        Text,  # JSON array stored as text
        nullable=True,
        comment="Tags for categorization and search"
    )
    
    priority: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="Priority level (1=low, 5=high)"
    )
    
    # Calendar integration
    calendar_event_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="External calendar event ID"
    )
    
    # Relationships
    # calendar_event: Mapped[Optional["CalendarEvent"]] = relationship(
    #     "CalendarEvent",
    #     foreign_keys=[calendar_event_id],
    #     back_populates="bookings"
    # )
    
    created_by_employee: Mapped[Optional["Employee"]] = relationship(
        "app.models.employee_enhanced.Employee",
        foreign_keys="Booking.created_by",
        back_populates="created_bookings"
    )
    
    updated_by_employee: Mapped[Optional["Employee"]] = relationship(
        "app.models.employee_enhanced.Employee",
        foreign_keys="Booking.updated_by",
        back_populates="updated_bookings"
    )
    
    # Table configuration
    __table_args__ = (
        # Composite indexes for common query patterns
        Index("idx_booking_date_time", "booking_date", "start_time", "end_time"),
        Index("idx_booking_state_date", "state", "booking_date"),
        Index("idx_booking_client_phone", "client_phone_normalized"),
        Index("idx_booking_space_type", "space_type", "booking_date"),
        Index("idx_booking_payment_status", "payment_status", "booking_date"),
        Index("idx_booking_priority", "priority", "booking_date"),
        
        # Check constraints
        CheckConstraint("end_time > start_time", name="check_time_validity"),
        CheckConstraint("duration_hours > 0", name="check_duration_positive"),
        CheckConstraint("base_price >= 0", name="check_base_price_non_negative"),
        CheckConstraint("equipment_price >= 0", name="check_equipment_price_non_negative"),
        CheckConstraint("discount_amount >= 0", name="check_discount_non_negative"),
        CheckConstraint("total_price >= 0", name="check_total_price_non_negative"),
        CheckConstraint("people_count > 0", name="check_people_count_positive"),
        CheckConstraint("priority >= 1 AND priority <= 5", name="check_priority_range"),
        
        # Unique constraints
        UniqueConstraint("booking_reference", name="uq_booking_reference"),
        
        # Extend existing table configuration
        {"extend_existing": True}
    )
    
    def __init__(self, **kwargs):
        """Initialize the booking with computed fields."""
        # Calculate duration if start and end times are provided
        if "start_time" in kwargs and "end_time" in kwargs:
            start = kwargs["start_time"]
            end = kwargs["end_time"]
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
            
            duration = (end - start).total_seconds() / 3600
            kwargs["duration_hours"] = round(duration, 2)
        
        # Calculate total price
        if "base_price" in kwargs:
            base_price = kwargs["base_price"]
            equipment_price = kwargs.get("equipment_price", 0)
            discount_amount = kwargs.get("discount_amount", 0)
            
            total = base_price + equipment_price - discount_amount
            kwargs["total_price"] = total
        
        # Generate booking reference if not provided
        if "booking_reference" not in kwargs:
            kwargs["booking_reference"] = self._generate_reference()
        
        super().__init__(**kwargs)
    
    # State machine methods
    def can_transition_to(self, target_state: BookingState) -> bool:
        """Check if transition to target state is valid."""
        valid_transitions = {
            BookingState.DRAFT: [BookingState.PENDING, BookingState.CANCELLED],
            BookingState.PENDING: [BookingState.CONFIRMED, BookingState.CANCELLED, BookingState.DRAFT],
            BookingState.CONFIRMED: [BookingState.IN_PROGRESS, BookingState.CANCELLED, BookingState.RESCHEDULED],
            BookingState.IN_PROGRESS: [BookingState.COMPLETED, BookingState.CANCELLED],
            BookingState.COMPLETED: [BookingState.CANCELLED],  # Can be cancelled for refunds
            BookingState.CANCELLED: [BookingState.PENDING],  # Can be reactivated
            BookingState.NO_SHOW: [BookingState.CANCELLED, BookingState.PENDING],
            BookingState.RESCHEDULED: [BookingState.CONFIRMED, BookingState.CANCELLED],
        }
        
        current_state = self.state
        allowed_transitions = valid_transitions.get(current_state, [])
        return target_state in allowed_transitions
    
    def transition_to(self, target_state: BookingState, user_id: int, reason: Optional[str] = None) -> bool:
        """
        Transition to a new state.
        
        Args:
            target_state: The target state to transition to
            user_id: ID of the user making the transition
            reason: Optional reason for the transition
            
        Returns:
            True if transition was successful, False otherwise
        """
        if not self.can_transition_to(target_state):
            return False
        
        # Record state history
        self._add_state_history(target_state, user_id, reason)
        
        # Update state
        old_state = self.state
        self.state = target_state
        
        # Handle state-specific side effects
        self._handle_state_side_effects(old_state, target_state, user_id)
        
        # Update audit trail
        self.update_audit_trail(
            "state_transition",
            user_id=user_id,
            details={
                "from_state": old_state.value,
                "to_state": target_state.value,
                "reason": reason
            }
        )
        
        # Increment version for optimistic locking
        self.increment_version()
        
        return True
    
    def _add_state_history(self, new_state: BookingState, user_id: int, reason: Optional[str] = None) -> None:
        """Add entry to state history."""
        if self.state_history is None:
            self.state_history = []
        
        # Parse existing history
        try:
            if isinstance(self.state_history, str):
                import json
                history = json.loads(self.state_history)
            else:
                history = self.state_history
        except (json.JSONDecodeError, TypeError):
            history = []
        
        # Add new entry
        entry = {
            "state": new_state.value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "reason": reason,
            "version": self.version
        }
        
        history.append(entry)
        
        # Keep only last 50 state changes
        if len(history) > 50:
            history = history[-50:]
        
        # Serialize to JSON string for database storage
        import json
        self.state_history = json.dumps(history)
    
    def _handle_state_side_effects(self, old_state: BookingState, new_state: BookingState, user_id: int) -> None:
        """Handle side effects of state transitions."""
        if new_state == BookingState.CONFIRMED:
            # Send confirmation notifications
            self._send_confirmation_notifications()
        
        elif new_state == BookingState.IN_PROGRESS:
            # Update calendar status
            self._update_calendar_status("in_progress")
        
        elif new_state == BookingState.COMPLETED:
            # Send completion notifications
            self._send_completion_notifications()
            # Update calendar status
            self._update_calendar_status("completed")
        
        elif new_state == BookingState.CANCELLED:
            # Send cancellation notifications
            self._send_cancellation_notifications()
            # Update calendar status
            self._update_calendar_status("cancelled")
            # Process refunds if needed
            self._process_cancellation_refund()
    
    def _send_confirmation_notifications(self) -> None:
        """Send confirmation notifications."""
        # This would integrate with notification service
        pass
    
    def _send_completion_notifications(self) -> None:
        """Send completion notifications."""
        # This would integrate with notification service
        pass
    
    def _send_cancellation_notifications(self) -> None:
        """Send cancellation notifications."""
        # This would integrate with notification service
        pass
    
    def _update_calendar_status(self, status: str) -> None:
        """Update external calendar status."""
        # This would integrate with calendar service
        pass
    
    def _process_cancellation_refund(self) -> None:
        """Process cancellation refunds."""
        # This would integrate with payment service
        pass
    
    # Validation methods
    def validate_booking(self) -> List[str]:
        """Validate booking data and return list of errors."""
        errors = []
        
        # Time validation
        if self.start_time >= self.end_time:
            errors.append("Start time must be before end time")
        
        if self.booking_date != self.start_time.date():
            errors.append("Booking date must match start time date")
        
        # Duration validation
        if self.duration_hours <= 0:
            errors.append("Duration must be positive")
        
        if self.duration_hours > 24:
            errors.append("Duration cannot exceed 24 hours")
        
        # Client validation
        if not self.client_name or len(self.client_name.strip()) < 2:
            errors.append("Client name must be at least 2 characters")
        
        if not self.client_phone or len(self.client_phone.strip()) < 10:
            errors.append("Valid phone number is required")
        
        # Price validation
        if self.base_price < 0:
            errors.append("Base price cannot be negative")
        
        if self.total_price < 0:
            errors.append("Total price cannot be negative")
        
        # People count validation
        if self.people_count <= 0:
            errors.append("People count must be positive")
        
        if self.people_count > 50:
            errors.append("People count cannot exceed 50")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if booking is valid."""
        return len(self.validate_booking()) == 0
    
    # Business logic methods
    def can_be_cancelled(self) -> bool:
        """Check if booking can be cancelled."""
        return self.state in [BookingState.PENDING, BookingState.CONFIRMED, BookingState.IN_PROGRESS]
    
    def can_be_rescheduled(self) -> bool:
        """Check if booking can be rescheduled."""
        return self.state in [BookingState.PENDING, BookingState.CONFIRMED]
    
    def is_overdue(self) -> bool:
        """Check if booking is overdue."""
        if self.state not in [BookingState.IN_PROGRESS]:
            return False
        
        # Consider overdue if more than 2 hours past end time
        overdue_threshold = self.end_time + timedelta(hours=2)
        return datetime.now(timezone.utc) > overdue_threshold
    
    def calculate_refund_amount(self) -> Decimal:
        """Calculate refund amount if cancelled."""
        if self.state != BookingState.CANCELLED:
            return Decimal('0')
        
        # Full refund if cancelled more than 24 hours before start
        cancellation_time = datetime.now(timezone.utc)
        hours_before_start = (self.start_time - cancellation_time).total_seconds() / 3600
        
        if hours_before_start >= 24:
            return self.total_price
        elif hours_before_start >= 2:
            return self.total_price * Decimal('0.5')  # 50% refund
        else:
            return Decimal('0')  # No refund
    
    def add_equipment(self, equipment: str, price: Decimal) -> None:
        """Add equipment to booking."""
        if self.equipment_requested is None:
            self.equipment_requested = {}
        
        # Parse existing equipment
        try:
            if isinstance(self.equipment_requested, str):
                import json
                equipment_dict = json.loads(self.equipment_requested)
            else:
                equipment_dict = self.equipment_requested
        except (json.JSONDecodeError, TypeError):
            equipment_dict = {}
        
        # Add equipment
        equipment_dict[equipment] = {
            "price": float(price),
            "added_at": datetime.now(timezone.utc).isoformat()
        }
        
        self.equipment_requested = equipment_dict
        self.equipment_price += price
        self.total_price += price
        
        # Update audit trail
        self.update_audit_trail(
            "equipment_added",
            user_id=0,  # System action
            details={"equipment": equipment, "price": float(price)}
        )
    
    def apply_discount(self, amount: Decimal, reason: str, user_id: int) -> None:
        """Apply discount to booking."""
        if amount > self.total_price:
            raise ValueError("Discount cannot exceed total price")
        
        self.discount_amount += amount
        self.total_price -= amount
        
        # Update audit trail
        self.update_audit_trail(
            "discount_applied",
            user_id=user_id,
            details={"amount": float(amount), "reason": reason}
        )
    
    def add_note(self, note: str, is_internal: bool = False, user_id: int = 0) -> None:
        """Add note to booking."""
        if is_internal:
            if self.internal_notes is None:
                self.internal_notes = ""
            self.internal_notes += f"\n[{datetime.now(timezone.utc).isoformat()}] {note}"
        else:
            if self.notes is None:
                self.notes = ""
            self.notes += f"\n[{datetime.now(timezone.utc).isoformat()}] {note}"
        
        # Update audit trail
        self.update_audit_trail(
            "note_added",
            user_id=user_id,
            details={"note": note, "is_internal": is_internal}
        )
    
    # Utility methods
    def _generate_reference(self) -> str:
        """Generate unique booking reference."""
        # Format: REF-YYYYMMDD-XXXX
        date_str = datetime.now().strftime("%Y%m%d")
        # In production, this would be generated with proper sequence
        sequence = "0001"  # This should come from database sequence
        return f"REF-{date_str}-{sequence}"
    
    def get_state_duration(self) -> Optional[timedelta]:
        """Get duration of current state."""
        if not self.state_history:
            return None
        
        try:
            if isinstance(self.state_history, str):
                import json
                history = json.loads(self.state_history)
            else:
                history = self.state_history
            
            if not history:
                return None
            
            # Find current state entry
            current_entry = None
            for entry in reversed(history):
                if entry.get("state") == self.state.value:
                    current_entry = entry
                    break
            
            if not current_entry:
                return None
            
            # Calculate duration
            state_start = datetime.fromisoformat(current_entry["timestamp"])
            return datetime.now(timezone.utc) - state_start
            
        except (json.JSONDecodeError, TypeError, KeyError):
            return None
    
    def get_total_duration(self) -> timedelta:
        """Get total duration from start to end."""
        return self.end_time - self.start_time
    
    def is_confirmed(self) -> bool:
        """Check if booking is confirmed."""
        return self.state in [BookingState.CONFIRMED, BookingState.IN_PROGRESS, BookingState.COMPLETED]
    
    def is_active(self) -> bool:
        """Check if booking is currently active."""
        return self.state in [BookingState.CONFIRMED, BookingState.IN_PROGRESS]
    
    def is_completed(self) -> bool:
        """Check if booking is completed."""
        return self.state == BookingState.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if booking is cancelled."""
        return self.state == BookingState.CANCELLED
    
    # Serialization methods
    def to_dict(self, include_history: bool = True) -> Dict[str, Any]:
        """Convert booking to dictionary."""
        result = super().to_dict()
        
        # Add booking-specific fields
        result.update({
            "booking_reference": self.booking_reference,
            "booking_date": self.booking_date.isoformat() if self.booking_date else None,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_hours": float(self.duration_hours) if self.duration_hours else 0,
            "state": self.state.value,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_phone_normalized": self.client_phone_normalized,
            "client_email": self.client_email,
            "space_type": self.space_type.value,
            "equipment_requested": self.equipment_requested,
            "special_requirements": self.special_requirements,
            "people_count": self.people_count,
            "base_price": float(self.base_price) if self.base_price else 0,
            "equipment_price": float(self.equipment_price) if self.equipment_price else 0,
            "discount_amount": float(self.discount_amount) if self.discount_amount else 0,
            "total_price": float(self.total_price) if self.total_price else 0,
            "payment_status": self.payment_status.value,
            "source": self.source.value,
            "notes": self.notes,
            "internal_notes": self.internal_notes,
            "tags": self.tags,
            "priority": self.priority,
            "calendar_event_id": self.calendar_event_id,
        })
        
        if include_history:
            result["state_history"] = self.state_history
            result["state_duration"] = self.get_state_duration().total_seconds() / 3600 if self.get_state_duration() else None
        
        return result
    
    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert booking to summary dictionary."""
        return {
            "id": self.id,
            "booking_reference": self.booking_reference,
            "client_name": self.client_name,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "state": self.state.value,
            "space_type": self.space_type.value,
            "total_price": float(self.total_price) if self.total_price else 0,
            "payment_status": self.payment_status.value,
            "priority": self.priority,
        }
    
    @classmethod
    def get_states(cls) -> List[str]:
        """Get list of available booking states."""
        return [state.value for state in BookingState]
    
    @classmethod
    def get_payment_statuses(cls) -> List[str]:
        """Get list of available payment statuses."""
        return [status.value for status in PaymentStatus]
    
    @classmethod
    def get_sources(cls) -> List[str]:
        """Get list of available booking sources."""
        return [source.value for source in BookingSource]
    
    @classmethod
    def get_space_types(cls) -> List[str]:
        """Get list of available space types."""
        return [space.value for space in SpaceType]