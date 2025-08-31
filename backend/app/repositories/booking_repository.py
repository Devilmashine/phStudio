from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime
from ..models.booking_enhanced import Booking, BookingState
from .base_repository import BaseRepository

class BookingRepository(BaseRepository[Booking]):
    """Repository for Booking entities"""
    
    def __init__(self, db: Session):
        from ..models.booking_enhanced import Booking
        super().__init__(db, Booking)
    
    def get_by_reference(self, reference: str) -> Optional[Booking]:
        """Get booking by reference"""
        return self.db.query(self.model).filter(self.model.booking_reference == reference).first()
    
    def get_by_client_phone(self, phone: str) -> List[Booking]:
        """Get bookings by client phone"""
        return self.db.query(self.model).filter(self.model.client_phone_normalized == phone).all()
    
    def get_by_state(self, state: BookingState) -> List[Booking]:
        """Get bookings by state"""
        return self.db.query(self.model).filter(self.model.state == state).all()
    
    def get_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Booking]:
        """Get bookings within date range"""
        return self.db.query(self.model).filter(
            and_(
                self.model.booking_date >= start_date,
                self.model.booking_date <= end_date
            )
        ).all()
    
    def get_recent_bookings(self, limit: int = 50) -> List[Booking]:
        """Get most recent bookings"""
        return self.db.query(self.model).order_by(desc(self.model.created_at)).limit(limit).all()
    
    def get_bookings_with_state_history(self, booking_id: int) -> Optional[Booking]:
        """Get booking with complete state history"""
        return self.db.query(self.model).filter(self.model.id == booking_id).first()