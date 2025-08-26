"""
Telegram API Routes

Comprehensive FastAPI endpoints for Telegram integration:
- Webhook processing
- Bot management
- Status monitoring
- Message sending
- Queue management
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.deps import get_current_admin
from app.models.user import User
from app.models.telegram import (
    TelegramMessage,
    MessageResult,
    MessagePriority,
    TemplateType,
    Language,
    BookingData
)
from app.services.telegram.service import telegram_service
from app.services.telegram.webhook_handler import webhook_handler
from app.services.telegram.booking_notifications import booking_notification_service
from app.services.telegram.message_queue import message_queue

logger = logging.getLogger(__name__)
security = HTTPBearer()
router = APIRouter()


class SendMessageRequest(BaseModel):
    """Request model for sending messages"""
    chat_id: str = Field(..., description="Telegram chat ID")
    text: str = Field(..., min_length=1, max_length=4096, description="Message text")
    parse_mode: Optional[str] = Field(default="HTML", description="Message parse mode")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Message priority")
    queue: bool = Field(default=True, description="Whether to queue the message")


class SendTemplatedMessageRequest(BaseModel):
    """Request model for sending templated messages"""
    template_type: TemplateType = Field(..., description="Template type")
    chat_id: str = Field(..., description="Telegram chat ID")
    template_data: Dict[str, Any] = Field(..., description="Template data")
    language: Language = Field(default=Language.RU, description="Language")
    priority: MessagePriority = Field(default=MessagePriority.NORMAL, description="Message priority")
    queue: bool = Field(default=True, description="Whether to queue the message")


class BookingNotificationRequest(BaseModel):
    """Request model for booking notifications"""
    booking_data: BookingData = Field(..., description="Booking information")
    language: Language = Field(default=Language.RU, description="Language")
    queue: bool = Field(default=True, description="Whether to queue the message")


class WebhookSetupRequest(BaseModel):
    """Request model for webhook setup"""
    url: str = Field(..., description="Webhook URL")
    secret_token: Optional[str] = Field(default=None, description="Secret token")


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Handle incoming Telegram webhook updates
    
    This endpoint processes incoming updates from Telegram including:
    - Text messages and commands
    - Callback queries from inline keyboards
    - Other update types
    """
    try:
        # Get raw payload for signature verification
        payload = await request.body()
        signature = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        
        # Verify webhook signature
        if not webhook_handler.verify_webhook_signature(payload, signature):
            logger.warning("Invalid webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        # Parse update data
        update_data = await request.json()
        
        # Process update in background to avoid timeout
        background_tasks.add_task(
            webhook_handler.process_update,
            update_data
        )
        
        return {"status": "ok"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in webhook endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/send", dependencies=[Depends(get_current_admin)])
async def send_message(
    message_request: SendMessageRequest
) -> Dict[str, Any]:
    """
    Send a message via Telegram (admin only)
    
    This endpoint allows administrators to send custom messages
    through the Telegram bot.
    """
    try:
        message = TelegramMessage(
            chat_id=message_request.chat_id,
            text=message_request.text,
            parse_mode=message_request.parse_mode,
            priority=message_request.priority
        )
        
        if message_request.queue:
            success = await telegram_service.queue_message(message)
            return {
                "success": success,
                "message_id": message.message_id if success else None,
                "queued": True,
                "error": None if success else "Failed to queue message"
            }
        else:
            result = await telegram_service.send_message(message)
            return {
                "success": result.success,
                "message_id": result.message_id,
                "telegram_message_id": result.telegram_message_id,
                "queued": False,
                "error": result.error
            }
            
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-templated", dependencies=[Depends(get_current_admin)])
async def send_templated_message(
    message_request: SendTemplatedMessageRequest
) -> Dict[str, Any]:
    """
    Send a templated message via Telegram (admin only)
    
    This endpoint allows sending messages using predefined templates
    with data substitution.
    """
    try:
        result = await telegram_service.send_templated_message(
            template_type=message_request.template_type,
            chat_id=message_request.chat_id,
            template_data=message_request.template_data,
            language=message_request.language,
            priority=message_request.priority,
            queue=message_request.queue
        )
        
        return {
            "success": result.success,
            "message_id": result.message_id,
            "telegram_message_id": result.telegram_message_id,
            "queued": message_request.queue,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"Error sending templated message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/booking-notification", dependencies=[Depends(get_current_admin)])
async def send_booking_notification(
    notification_request: BookingNotificationRequest
) -> Dict[str, Any]:
    """
    Send booking notification (admin only)
    
    This endpoint sends a formatted booking notification with
    action buttons to the admin chat.
    """
    try:
        result = await booking_notification_service.send_booking_notification(
            booking_data=notification_request.booking_data,
            language=notification_request.language,
            queue=notification_request.queue
        )
        
        return {
            "success": result.success,
            "message_id": result.message_id,
            "telegram_message_id": result.telegram_message_id,
            "queued": notification_request.queue,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"Error sending booking notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_bot_status() -> Dict[str, Any]:
    """
    Get bot information and connectivity status
    
    This endpoint provides comprehensive information about:
    - Bot connectivity
    - Service health
    - Queue metrics
    - Performance statistics
    """
    try:
        health = await telegram_service.get_service_health()
        webhook_metrics = webhook_handler.get_metrics()
        notification_metrics = booking_notification_service.get_metrics()
        
        # Try to get bot info
        bot_info = None
        try:
            bot_info_obj = await telegram_service.get_bot_info()
            bot_info = bot_info_obj.dict()
        except Exception as e:
            logger.warning(f"Could not get bot info: {e}")
        
        return {
            "status": health["status"],
            "bot_info": bot_info,
            "service_health": health,
            "webhook_metrics": webhook_metrics,
            "notification_metrics": notification_metrics,
            "webhook_configured": bool(get_settings().TELEGRAM_WEBHOOK_URL)
        }
        
    except Exception as e:
        logger.error(f"Error getting bot status: {e}")
        return {
            "status": "error",
            "error": str(e),
            "bot_info": None,
            "webhook_configured": False
        }


@router.post("/webhook/setup", dependencies=[Depends(get_current_admin)])
async def setup_webhook(
    webhook_request: WebhookSetupRequest
) -> Dict[str, Any]:
    """
    Set up webhook for the bot (admin only)
    
    This endpoint configures the webhook URL for receiving
    updates from Telegram.
    """
    try:
        success = await telegram_service.set_webhook(
            url=webhook_request.url,
            secret_token=webhook_request.secret_token or ""
        )
        
        return {
            "success": success,
            "webhook_url": webhook_request.url if success else None,
            "message": "Webhook set successfully" if success else "Failed to set webhook"
        }
        
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/webhook", dependencies=[Depends(get_current_admin)])
async def delete_webhook() -> Dict[str, Any]:
    """
    Delete webhook for the bot (admin only)
    
    This endpoint removes the current webhook configuration.
    """
    try:
        success = await telegram_service.delete_webhook()
        
        return {
            "success": success,
            "message": "Webhook deleted successfully" if success else "Failed to delete webhook"
        }
        
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/metrics", dependencies=[Depends(get_current_admin)])
async def get_queue_metrics() -> Dict[str, Any]:
    """
    Get message queue metrics (admin only)
    
    This endpoint provides detailed information about the
    message queue performance and status.
    """
    try:
        metrics = await telegram_service.get_queue_metrics()
        return metrics.dict()
        
    except Exception as e:
        logger.error(f"Error getting queue metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queue/dlq", dependencies=[Depends(get_current_admin)])
async def get_dlq_messages(
    limit: int = 10
) -> Dict[str, Any]:
    """
    Get messages from dead letter queue (admin only)
    
    This endpoint returns messages that failed to send
    after all retry attempts.
    """
    try:
        dlq_messages = await message_queue.get_dlq_messages(limit)
        
        return {
            "messages": dlq_messages,
            "count": len(dlq_messages),
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Error getting DLQ messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/queue/dlq/requeue/{index}", dependencies=[Depends(get_current_admin)])
async def requeue_dlq_message(
    index: int
) -> Dict[str, Any]:
    """
    Requeue a message from dead letter queue (admin only)
    
    This endpoint moves a failed message back to the main queue
    for another attempt.
    """
    try:
        success = await message_queue.requeue_dlq_message(index)
        
        return {
            "success": success,
            "message": "Message requeued successfully" if success else "Failed to requeue message"
        }
        
    except Exception as e:
        logger.error(f"Error requeuing DLQ message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/queue/dlq", dependencies=[Depends(get_current_admin)])
async def clear_dlq() -> Dict[str, Any]:
    """
    Clear all messages from dead letter queue (admin only)
    
    This endpoint removes all failed messages from the DLQ.
    Use with caution as this cannot be undone.
    """
    try:
        count = await message_queue.clear_dlq()
        
        return {
            "success": True,
            "cleared_count": count,
            "message": f"Cleared {count} messages from DLQ"
        }
        
    except Exception as e:
        logger.error(f"Error clearing DLQ: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/worker/start", dependencies=[Depends(get_current_admin)])
async def start_background_worker() -> Dict[str, Any]:
    """
    Start background message worker (admin only)
    
    This endpoint starts the background worker that processes
    queued messages.
    """
    try:
        await telegram_service.start_background_worker()
        
        return {
            "success": True,
            "message": "Background worker started"
        }
        
    except Exception as e:
        logger.error(f"Error starting background worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/worker/stop", dependencies=[Depends(get_current_admin)])
async def stop_background_worker() -> Dict[str, Any]:
    """
    Stop background message worker (admin only)
    
    This endpoint stops the background worker that processes
    queued messages.
    """
    try:
        await telegram_service.stop_background_worker()
        
        return {
            "success": True,
            "message": "Background worker stopped"
        }
        
    except Exception as e:
        logger.error(f"Error stopping background worker: {e}")
        raise HTTPException(status_code=500, detail=str(e))
