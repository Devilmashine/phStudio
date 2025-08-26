"""
Core Telegram integration models and protocols.

This module defines the data structures and protocols for the refactored
Telegram integration system, providing type safety and validation.
"""

from typing import Optional, Dict, Any, List, Protocol, runtime_checkable
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
import uuid


class MessagePriority(str, Enum):
    """Message priority levels for queue processing"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class MessageStatus(str, Enum):
    """Message processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


class Language(str, Enum):
    """Supported languages for templates"""
    RU = "ru"
    EN = "en"


class TemplateType(str, Enum):
    """Available message templates"""
    BOOKING_NOTIFICATION = "booking_notification"
    BOOKING_CONFIRMATION = "booking_confirmation"
    BOOKING_CANCELLATION = "booking_cancellation"
    BOOKING_REMINDER = "booking_reminder"
    BOOKING_UPDATE = "booking_update"
    SYSTEM_NOTIFICATION = "system_notification"


class TelegramMessage(BaseModel):
    """Structured Telegram message model with validation"""
    
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    chat_id: str = Field(..., description="Telegram chat ID")
    text: str = Field(..., min_length=1, max_length=4096, description="Message text")
    parse_mode: Optional[str] = Field(default="HTML", description="Message parse mode")
    reply_markup: Optional[Dict[str, Any]] = Field(default=None, description="Inline keyboard markup")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL)
    status: MessageStatus = Field(default=MessageStatus.PENDING)
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    scheduled_at: Optional[datetime] = Field(default=None)
    sent_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)
    
    # Template metadata
    template_type: Optional[TemplateType] = Field(default=None)
    template_data: Optional[Dict[str, Any]] = Field(default=None)
    language: Language = Field(default=Language.RU)
    
    @validator('chat_id')
    def validate_chat_id(cls, v):
        if not v or (not v.startswith('-') and not v.isdigit()):
            raise ValueError('Invalid chat ID format')
        return v
    
    @validator('text')
    def validate_text_length(cls, v):
        if len(v.encode('utf-8')) > 4096:
            raise ValueError('Message text too long (max 4096 bytes)')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class MessageResult(BaseModel):
    """Result of message sending operation"""
    
    success: bool
    message_id: Optional[str] = None
    telegram_message_id: Optional[int] = None
    error: Optional[str] = None
    retry_after: Optional[int] = None
    sent_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BotInfo(BaseModel):
    """Telegram bot information"""
    
    id: int
    is_bot: bool
    first_name: str
    username: Optional[str] = None
    can_join_groups: Optional[bool] = None
    can_read_all_group_messages: Optional[bool] = None
    supports_inline_queries: Optional[bool] = None


class WebhookUpdate(BaseModel):
    """Telegram webhook update structure"""
    
    update_id: int
    message: Optional[Dict[str, Any]] = None
    callback_query: Optional[Dict[str, Any]] = None
    edited_message: Optional[Dict[str, Any]] = None
    
    @property
    def has_message(self) -> bool:
        return self.message is not None
    
    @property
    def has_callback_query(self) -> bool:
        return self.callback_query is not None
    
    @property
    def chat_id(self) -> Optional[str]:
        if self.message:
            return str(self.message["chat"]["id"])
        elif self.callback_query:
            return str(self.callback_query["message"]["chat"]["id"])
        return None


class QueueMetrics(BaseModel):
    """Message queue metrics"""
    
    pending_messages: int = 0
    processing_messages: int = 0
    failed_messages: int = 0
    dead_letter_messages: int = 0
    total_processed: int = 0
    average_processing_time: float = 0.0
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class BookingData(BaseModel):
    """Booking data for notifications"""
    
    id: str
    service: str
    date: datetime
    time_slots: List[str]
    client_name: str
    client_phone: str
    people_count: int
    total_price: float
    description: Optional[str] = None
    status: str = "pending"


@runtime_checkable
class TelegramServiceProtocol(Protocol):
    """Protocol for Telegram service implementations"""
    
    async def send_message(self, message: TelegramMessage) -> MessageResult:
        """Send a single message"""
        ...
    
    async def send_message_batch(self, messages: List[TelegramMessage]) -> List[MessageResult]:
        """Send multiple messages"""
        ...
    
    async def get_bot_info(self) -> BotInfo:
        """Get bot information"""
        ...
    
    async def set_webhook(self, url: str, secret_token: str) -> bool:
        """Set webhook URL"""
        ...
    
    async def delete_webhook(self) -> bool:
        """Delete webhook"""
        ...


@runtime_checkable
class MessageQueueProtocol(Protocol):
    """Protocol for message queue implementations"""
    
    async def enqueue_message(self, message: TelegramMessage) -> bool:
        """Add message to queue"""
        ...
    
    async def dequeue_message(self) -> Optional[TelegramMessage]:
        """Get next message from queue"""
        ...
    
    async def move_to_dlq(self, message: TelegramMessage, error: str) -> bool:
        """Move message to dead letter queue"""
        ...
    
    async def get_queue_metrics(self) -> QueueMetrics:
        """Get queue metrics"""
        ...


@runtime_checkable
class TemplateEngineProtocol(Protocol):
    """Protocol for template engine implementations"""
    
    def render_template(
        self, 
        template_type: TemplateType, 
        language: Language, 
        **kwargs
    ) -> str:
        """Render template with data"""
        ...
    
    def validate_template_data(
        self, 
        template_type: TemplateType, 
        data: Dict[str, Any]
    ) -> bool:
        """Validate template data"""
        ...


class TelegramError(Exception):
    """Base Telegram integration error"""
    pass


class TelegramAPIError(TelegramError):
    """Telegram API specific error"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class TelegramConfigError(TelegramError):
    """Telegram configuration error"""
    pass


class TelegramQueueError(TelegramError):
    """Message queue error"""
    pass


class TelegramTemplateError(TelegramError):
    """Template rendering error"""
    pass