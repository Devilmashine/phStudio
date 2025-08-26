"""
Basic Test Suite for Telegram Integration

Simple tests to verify the refactored Telegram integration system works.
"""

import pytest
from datetime import datetime
from unittest.mock import MagicMock

from app.models.telegram import (
    TelegramMessage,
    MessagePriority,
    TemplateType,
    Language,
    BookingData
)
from app.services.telegram.template_engine import template_engine


class TestTelegramTemplateEngine:
    """Test template engine functionality"""
    
    def test_render_booking_notification_template(self):
        """Test rendering booking notification template"""
        template_data = {
            "service": "Студийная фотосессия",
            "date": "15.12.2024",
            "times": ["10:00", "12:00"],
            "client_name": "Иван Иванов",
            "client_phone": "+79991234567",
            "people_count": 2,
            "total_price": 5000,
            "booking_id": "123"
        }
        
        result = template_engine.render_template(
            TemplateType.BOOKING_NOTIFICATION,
            Language.RU,
            **template_data
        )
        
        assert "🎨" in result
        assert "Новое бронирование" in result
        assert "Студийная фотосессия" in result
        assert "15.12.2024" in result
        assert "Иван Иванов" in result
        assert "+79991234567" in result
        assert "5000 руб." in result
        assert "10:00, 12:00" in result
    
    def test_render_confirmation_template(self):
        """Test rendering booking confirmation template"""
        template_data = {
            "booking_id": "123",
            "client_name": "Иван Иванов",
            "date": "15.12.2024",
            "time": "10:00-12:00",
            "confirmed_at": datetime.now()
        }
        
        result = template_engine.render_template(
            TemplateType.BOOKING_CONFIRMATION,
            Language.RU,
            **template_data
        )
        
        assert "✅ Бронирование подтверждено" in result
        assert "123" in result
        assert "Иван Иванов" in result
    
    def test_english_template(self):
        """Test English template rendering"""
        template_data = {
            "service": "Studio Photoshoot",
            "date": "15.12.2024",
            "times": ["10:00"],
            "client_name": "John Doe",
            "client_phone": "+79991234567",
            "people_count": 1,
            "total_price": 5000,
            "booking_id": "123"
        }
        
        result = template_engine.render_template(
            TemplateType.BOOKING_NOTIFICATION,
            Language.EN,
            **template_data
        )
        
        assert "🎨" in result
        assert "New Booking" in result
        assert "Studio Photoshoot" in result
        assert "John Doe" in result


class TestTelegramMessage:
    """Test Telegram message models"""
    
    def test_telegram_message_creation(self):
        """Test creating a TelegramMessage"""
        message = TelegramMessage(
            chat_id="123",
            text="Test message",
            priority=MessagePriority.HIGH
        )
        
        assert message.chat_id == "123"
        assert message.text == "Test message"
        assert message.priority == MessagePriority.HIGH
        assert message.parse_mode == "HTML"
    
    def test_booking_data_creation(self):
        """Test creating BookingData"""
        booking_data = BookingData(
            id="123",
            service="Test Service",
            date=datetime.now(),
            time_slots=["10:00-12:00"],
            client_name="Test Client",
            client_phone="+79991234567",
            people_count=1,
            total_price=5000,
            status="pending"
        )
        
        assert booking_data.id == "123"
        assert booking_data.service == "Test Service"
        assert booking_data.client_name == "Test Client"
        assert booking_data.total_price == 5000


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])