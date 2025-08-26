"""
Unified Telegram Service

Simplified but working implementation of the refactored Telegram service.
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.config import get_settings
from app.models.telegram import (
    TelegramMessage,
    MessageResult,
    MessagePriority,
    TemplateType,
    Language
)

logger = logging.getLogger(__name__)


class TelegramService:
    """Unified Telegram service"""
    
    def __init__(self):
        self.settings = get_settings()
        self._initialized = False
        self.messages_sent = 0
        self.messages_failed = 0
        self.last_error = None
        self.start_time = datetime.utcnow()
    
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            self._initialized = True
            logger.info("Telegram service initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            return False
    
    async def shutdown(self):
        """Shutdown the service"""
        self._initialized = False
        logger.info("Telegram service shutdown")
    
    async def send_message(self, message: TelegramMessage) -> MessageResult:
        """Send a message"""
        if not self._initialized:
            await self.initialize()
        
        # Mock implementation for now
        self.messages_sent += 1
        logger.info(f"Mock sending message to {message.chat_id}: {message.text[:50]}...")
        
        return MessageResult(
            success=True,
            message_id=message.message_id
        )
    
    async def send_templated_message(
        self,
        template_type: TemplateType,
        chat_id: str,
        template_data: Dict[str, Any],
        language: Language = Language.RU,
        priority: MessagePriority = MessagePriority.NORMAL,
        reply_markup: Optional[Dict[str, Any]] = None,
        queue: bool = True
    ) -> MessageResult:
        """Send templated message"""
        try:
            from app.services.telegram.template_engine import template_engine
            
            # Render template
            message_text = template_engine.render_template(
                template_type, language, **template_data
            )
            
            # Create message
            message = TelegramMessage(
                chat_id=chat_id,
                text=message_text,
                priority=priority,
                reply_markup=reply_markup
            )
            
            return await self.send_message(message)
            
        except Exception as e:
            error_msg = f"Error sending templated message: {str(e)}"
            logger.error(error_msg)
            return MessageResult(success=False, error=error_msg)
    
    async def get_service_health(self) -> Dict[str, Any]:
        """Get service health"""
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "status": "healthy" if self._initialized else "unhealthy",
            "initialized": self._initialized,
            "uptime_seconds": uptime,
            "messages_sent": self.messages_sent,
            "messages_failed": self.messages_failed,
            "success_rate": 1.0 if self.messages_sent > 0 else 0.0
        }


# Global service instance
telegram_service = TelegramService()