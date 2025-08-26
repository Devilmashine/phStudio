"""
Booking Notification Service

High-level service for sending booking-related notifications via Telegram.
Integrates with the template engine, message queue, and unified Telegram service.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.core.config import get_settings
from app.models.telegram import (
    TelegramMessage,
    MessageResult,
    MessagePriority,
    TemplateType,
    Language,
    BookingData
)
from app.services.telegram_bot import TelegramBotService

logger = logging.getLogger(__name__)


class BookingNotificationService:
    """
    High-level service for booking notifications with features:
    - Template-based message generation
    - Priority-based message routing
    - Comprehensive error handling
    - Metrics collection
    - Booking state management
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.telegram_bot_service = TelegramBotService()
        
        # Metrics
        self.notifications_sent = 0
        self.notifications_failed = 0
        self.last_notification_time = None
    
    async def send_booking_notification(
        self,
        booking_data: BookingData,
        language: Language = Language.RU,
        queue: bool = True
    ) -> MessageResult:
        """
        Send new booking notification to admin chat
        
        Args:
            booking_data: Booking information
            language: Language for notification
            queue: Whether to queue the message
            
        Returns:
            MessageResult with send status
        """
        try:
            # Use the real TelegramBotService to send notification
            success = await self.telegram_bot_service.send_booking_notification(
                message="Новое бронирование",
                booking_id=booking_data.id,
                service=booking_data.service,
                date=booking_data.date.strftime("%d.%m.%Y"),
                times=booking_data.time_slots,
                name=booking_data.client_name,
                phone=booking_data.client_phone,
                total_price=int(booking_data.total_price),
                people_count=booking_data.people_count
            )
            
            if success:
                self.notifications_sent += 1
                self.last_notification_time = datetime.utcnow()
                logger.info(f"Booking notification sent for booking {booking_data.id}")
                return MessageResult(success=True, message_id=booking_data.id)
            else:
                self.notifications_failed += 1
                logger.error(f"Failed to send booking notification for {booking_data.id}")
                return MessageResult(success=False, error="Failed to send Telegram message")
            
        except Exception as e:
            error_msg = f"Error sending booking notification: {str(e)}"
            logger.error(error_msg)
            self.notifications_failed += 1
            return MessageResult(success=False, error=error_msg)
    
    def _prepare_booking_template_data(self, booking_data: BookingData) -> Dict[str, Any]:
        """
        Prepare template data for booking notifications
        
        Args:
            booking_data: Booking information
            
        Returns:
            Dictionary with template data
        """
        # Format date as DD.MM.YYYY
        formatted_date = booking_data.date.strftime("%d.%m.%Y")
        
        # Format phone number
        formatted_phone = booking_data.client_phone
        if not formatted_phone.startswith("+"):
            formatted_phone = "+" + formatted_phone
        
        return {
            "booking_id": booking_data.id,
            "service": booking_data.service,
            "date": formatted_date,
            "times": booking_data.time_slots,
            "client_name": booking_data.client_name,
            "client_phone": formatted_phone,
            "people_count": booking_data.people_count,
            "total_price": booking_data.total_price,
            "description": booking_data.description,
            "status": booking_data.status
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get notification service metrics
        
        Returns:
            Dictionary with metrics
        """
        total_notifications = self.notifications_sent + self.notifications_failed
        success_rate = self.notifications_sent / max(total_notifications, 1)
        
        return {
            "notifications_sent": self.notifications_sent,
            "notifications_failed": self.notifications_failed,
            "total_notifications": total_notifications,
            "success_rate": success_rate,
            "last_notification_time": self.last_notification_time.isoformat() if self.last_notification_time else None
        }


# Global notification service instance
booking_notification_service = BookingNotificationService()