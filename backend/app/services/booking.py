from datetime import datetime, timezone, timedelta
import logging
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import and_, or_, func, text
from typing import List, Optional, Dict, Any

from app.models.booking import BookingLegacy as BookingModel, BookingStatus
from app.schemas.booking import BookingCreate
from app.services.telegram_bot import TelegramBotService
from app.core.errors import BookingError, ErrorHandler, handle_database_error, handle_not_found_error
from app.utils.timezone import from_moscow_time, to_moscow_time, get_moscow_now

# Import WebSocket manager
from app.core.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


class BookingService:
    """Service for managing booking operations with comprehensive error handling"""
    
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_booking(self, booking_id: int) -> Optional[BookingModel]:
        """Get booking by ID with error handling"""
        try:
            with ErrorHandler(f"get_booking({booking_id})", "BookingService"):
                return self.db.query(BookingModel).filter(BookingModel.id == booking_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving booking {booking_id}: {e}")
            raise handle_database_error(e, f"retrieving booking {booking_id}")

    def get_bookings(self, skip: int = 0, limit: int = 100) -> List[BookingModel]:
        """Get list of bookings with error handling and validation"""
        if skip < 0 or limit <= 0 or limit > 1000:
            raise BookingError("Invalid pagination parameters", "INVALID_PAGINATION")
        
        try:
            with ErrorHandler("get_bookings", "BookingService"):
                return self.db.query(BookingModel).offset(skip).limit(limit).all()
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving bookings: {e}")
            raise handle_database_error(e, "retrieving bookings list")

    def create_booking(self, booking_data: BookingCreate) -> BookingModel:
        """Create new booking with comprehensive validation and error handling"""
        try:
            with ErrorHandler("create_booking", "BookingService"):
                # Validate booking data
                if not booking_data.client_name or not booking_data.client_name.strip():
                    raise BookingError("Client name is required", "MISSING_CLIENT_NAME")
                
                if not booking_data.client_phone or not booking_data.client_phone.strip():
                    raise BookingError("Client phone is required", "MISSING_CLIENT_PHONE")
                
                if booking_data.start_time >= booking_data.end_time:
                    raise BookingError("Start time must be before end time", "INVALID_TIME_RANGE")
                
                # Validate that bookings are only at full hours
                start_moscow = to_moscow_time(booking_data.start_time)
                end_moscow = to_moscow_time(booking_data.end_time)
                
                if start_moscow.minute != 0 or start_moscow.second != 0 or start_moscow.microsecond != 0:
                    raise BookingError("Bookings must start at full hours (e.g., 10:00, 11:00)", "INVALID_START_TIME")
                
                if end_moscow.minute != 0 or end_moscow.second != 0 or end_moscow.microsecond != 0:
                    raise BookingError("Bookings must end at full hours (e.g., 11:00, 12:00)", "INVALID_END_TIME")
                
                # Check for time conflicts with existing bookings
                conflicting_bookings = self.db.query(BookingModel).filter(
                    and_(
                        BookingModel.start_time < booking_data.end_time,
                        BookingModel.end_time > booking_data.start_time
                        # Temporarily removed status filter due to enum issue
                    )
                ).all()
                
                if conflicting_bookings:
                    conflict_details = []
                    for booking in conflicting_bookings:
                        conflict_details.append(
                            f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"
                        )
                    
                    raise BookingError(
                        f"Time conflict detected. The following slots are already booked: {', '.join(conflict_details)}",
                        "TIME_CONFLICT"
                    )
                
                # Create booking
                booking = BookingModel(**booking_data.dict())
                self.db.add(booking)
                self.db.commit()
                self.db.refresh(booking)
                
                logger.info(f"Created booking {booking.id} for client {booking.client_name}")
                
                # Send WebSocket notification about new booking
                self._send_booking_notification(booking, "created")
                
                return booking
                
        except BookingError:
            # Re-raise custom booking errors
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating booking: {e}")
            raise handle_database_error(e, "creating booking")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating booking: {e}")
            raise BookingError(f"Failed to create booking: {str(e)}", "CREATION_FAILED")

    def update_booking_status(self, booking_id: int, status) -> Optional[BookingModel]:
        booking = self.get_booking(booking_id)
        if not booking:
            return None
        if isinstance(status, BookingStatus):
            setattr(booking, "status", status.value)
        elif isinstance(status, str):
            setattr(booking, "status", status)
        else:
            raise ValueError("Некорректный тип статуса бронирования")
        self.db.commit()
        self.db.refresh(booking)
        
        # Send WebSocket notification about booking update
        self._send_booking_notification(booking, "status_updated")
        
        return booking

    def delete_booking(self, booking_id: int) -> bool:
        booking = self.get_booking(booking_id)
        if not booking:
            return False
        self.db.delete(booking)
        self.db.commit()
        
        # Send WebSocket notification about booking deletion
        self._send_booking_notification(booking, "deleted")
        
        return True

    def update_booking(self, booking_id: int, booking_data: BookingCreate) -> Optional[BookingModel]:
        booking = self.get_booking(booking_id)
        if not booking:
            return None
        for field, value in booking_data.dict(exclude_unset=True).items():
            setattr(booking, field, value)
        self.db.commit()
        self.db.refresh(booking)
        
        # Send WebSocket notification about booking update
        self._send_booking_notification(booking, "updated")
        
        return booking

    def _send_booking_notification(self, booking: BookingModel, action: str):
        """Send WebSocket notification about booking changes"""
        try:
            import asyncio
            
            # Create notification message
            message = {
                "type": "booking_update",
                "action": action,
                "booking_id": booking.id,
                "client_name": booking.client_name,
                "status": booking.status,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Broadcast to notifications room
            # Using asyncio.create_task to avoid blocking the main thread
            asyncio.create_task(
                ws_manager.broadcast_to_room("notifications", message)
            )
        except Exception as e:
            logger.error(f"Failed to send WebSocket notification for booking {booking.id}: {e}")

    async def create_booking_with_notification(self, booking_data: BookingCreate) -> BookingModel:
        """Create booking and send Telegram notification using new system"""
        from app.services.telegram.booking_notifications import booking_notification_service
        from app.models.telegram import BookingData, Language
        
        # Create booking first
        booking = self.create_booking(booking_data)
        
        try:
            # Prepare booking data for notification
            notification_booking_data = BookingData(
                id=str(booking.id),
                service="Студийная фотосессия",  # Default service name
                date=booking.date,
                time_slots=[f"{booking.start_time.strftime('%H:%M')}-{booking.end_time.strftime('%H:%M')}"],
                client_name=booking.client_name,
                client_phone=booking.client_phone,
                people_count=getattr(booking, 'people_count', 1),  # Default to 1 if not set
                total_price=float(booking.total_price),
                description=booking.description,
                status="pending"
            )
            
            # Send notification using new system
            result = await booking_notification_service.send_booking_notification(
                booking_data=notification_booking_data,
                language=Language.RU,
                queue=True  # Use queue for reliability
            )
            
            if result.success:
                logger.info(f"Notification sent for booking {booking.id} (message_id: {result.message_id})")
            else:
                logger.error(f"Failed to send notification for booking {booking.id}: {result.error}")
                
        except Exception as e:
            logger.error(f"Failed to send notification for booking {booking.id}: {e}")
            # Don't fail the booking creation if notification fails
        
        return booking

    def get_bookings_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime, 
        status_filter: Optional[BookingStatus] = None
    ) -> List[BookingModel]:
        """Get bookings within date range with optimized query using indexes"""
        try:
            with ErrorHandler("get_bookings_by_date_range", "BookingService"):
                query = self.db.query(BookingModel).filter(
                    and_(
                        BookingModel.start_time >= start_date,
                        BookingModel.end_time <= end_date
                    )
                ).order_by(BookingModel.start_time)
                
                if status_filter:
                    query = query.filter(BookingModel.status == status_filter)
                
                return query.all()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in date range query: {e}")
            raise handle_database_error(e, "querying bookings by date range")

    def search_bookings_by_client(
        self, 
        search_term: str, 
        limit: int = 50
    ) -> List[BookingModel]:
        """Search bookings by client name or phone with optimized query"""
        if not search_term or len(search_term.strip()) < 2:
            raise BookingError("Search term must be at least 2 characters", "INVALID_SEARCH_TERM")
        
        try:
            with ErrorHandler("search_bookings_by_client", "BookingService"):
                search_pattern = f"%{search_term.strip()}%"
                
                # Use optimized query with proper indexes
                return self.db.query(BookingModel).filter(
                    or_(
                        BookingModel.client_name.ilike(search_pattern),
                        BookingModel.client_phone.like(search_pattern),
                        BookingModel.phone_normalized.like(search_pattern.replace("-", "").replace(" ", ""))
                    )
                ).order_by(BookingModel.created_at.desc()).limit(limit).all()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in client search: {e}")
            raise handle_database_error(e, "searching bookings by client")

    def get_booking_statistics(self, days_back: int = 30) -> Dict[str, Any]:
        """Get booking statistics with optimized aggregation queries"""
        try:
            with ErrorHandler("get_booking_statistics", "BookingService"):
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
                
                # Use optimized aggregation query - fixed table name to bookings_legacy
                stats_result = self.db.execute(text("""
                    SELECT 
                        COUNT(*) as total_bookings,
                        COUNT(CASE WHEN status = 'COMPLETED' THEN 1 END) as completed_bookings,
                        COUNT(CASE WHEN status = 'PENDING' THEN 1 END) as pending_bookings,
                        COUNT(CASE WHEN status = 'CANCELLED' THEN 1 END) as cancelled_bookings,
                        COALESCE(SUM(total_price), 0) as total_revenue,
                        COALESCE(AVG(total_price), 0) as average_price,
                        COUNT(DISTINCT client_phone) as unique_clients
                    FROM bookings_legacy 
                    WHERE created_at >= :cutoff_date
                """), {"cutoff_date": cutoff_date}).fetchone()
                
                if stats_result:
                    return {
                        "period_days": days_back,
                        "total_bookings": stats_result.total_bookings,
                        "completed_bookings": stats_result.completed_bookings,
                        "pending_bookings": stats_result.pending_bookings,
                        "cancelled_bookings": stats_result.cancelled_bookings,
                        "total_revenue": float(stats_result.total_revenue),
                        "average_price": float(stats_result.average_price),
                        "unique_clients": stats_result.unique_clients,
                        "completion_rate": (
                            stats_result.completed_bookings / stats_result.total_bookings 
                            if stats_result.total_bookings > 0 else 0
                        )
                    }
                
                return {"period_days": days_back, "total_bookings": 0}
                
        except SQLAlchemyError as e:
            logger.error(f"Database error in booking statistics: {e}")
            raise handle_database_error(e, "calculating booking statistics")

    def get_upcoming_bookings(self, hours_ahead: int = 24) -> List[BookingModel]:
        """Get upcoming bookings with optimized query using date index"""
        try:
            with ErrorHandler("get_upcoming_bookings", "BookingService"):
                cutoff_time = datetime.now(timezone.utc) + timedelta(hours=hours_ahead)
                
                return self.db.query(BookingModel).filter(
                    and_(
                        BookingModel.start_time >= datetime.now(timezone.utc),
                        BookingModel.start_time <= cutoff_time,
                        BookingModel.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
                    )
                ).order_by(BookingModel.start_time).all()
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting upcoming bookings: {e}")
            raise handle_database_error(e, "getting upcoming bookings")