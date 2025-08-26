"""
Redis-based Message Queue for Telegram Integration

Enterprise-grade message queue with features:
- Redis-backed persistence
- Retry mechanisms with exponential backoff
- Dead letter queue for failed messages
- Priority queue support
- Comprehensive metrics and monitoring
- Circuit breaker pattern for resilience
"""

import asyncio
import json
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import redis.asyncio as redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

from app.core.config import get_settings
from app.models.telegram import (
    TelegramMessage, 
    MessageStatus, 
    MessagePriority,
    QueueMetrics,
    TelegramQueueError,
    MessageQueueProtocol
)

logger = logging.getLogger(__name__)


class TelegramMessageQueue:
    """
    Redis-based message queue with enterprise features:
    - Priority-based processing
    - Automatic retry with exponential backoff
    - Dead letter queue for failed messages
    - Comprehensive metrics collection
    - Circuit breaker for Redis failures
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.redis_client: Optional[redis.Redis] = None
        self._circuit_breaker = CircuitBreaker()
        self._metrics = QueueMetrics()
        
        # Queue names
        self.queue_name = self.settings.TELEGRAM_QUEUE_NAME
        self.dlq_name = self.settings.TELEGRAM_DLQ_NAME
        self.processing_set = f"{self.queue_name}:processing"
        self.metrics_key = f"{self.queue_name}:metrics"
        
        # Priority queues
        self.priority_queues = {
            MessagePriority.CRITICAL: f"{self.queue_name}:critical",
            MessagePriority.HIGH: f"{self.queue_name}:high", 
            MessagePriority.NORMAL: f"{self.queue_name}:normal",
            MessagePriority.LOW: f"{self.queue_name}:low"
        }
    
    async def initialize(self) -> bool:
        """Initialize Redis connection and setup"""
        try:
            self.redis_client = redis.from_url(
                self.settings.REDIS_URL,
                decode_responses=True,
                retry_on_timeout=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis_client.ping()
            
            # Initialize metrics if not exists
            await self._initialize_metrics()
            
            logger.info("Telegram message queue initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize message queue: {e}")
            return False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def enqueue_message(self, message: TelegramMessage) -> bool:
        """
        Add message to appropriate priority queue
        
        Args:
            message: Telegram message to enqueue
            
        Returns:
            True if message was enqueued successfully
        """
        if not await self._circuit_breaker.call(self._is_redis_available):
            logger.error("Redis circuit breaker is open, rejecting message")
            return False
        
        try:
            # Prepare message data
            message.status = MessageStatus.PENDING
            message_data = message.json()
            
            # Get appropriate queue based on priority
            queue_name = self.priority_queues.get(message.priority, self.priority_queues[MessagePriority.NORMAL])
            
            # Add to queue with score for FIFO within priority
            score = datetime.utcnow().timestamp()
            await self.redis_client.zadd(queue_name, {message_data: score})
            
            # Update metrics
            await self._increment_metric("pending_messages")
            
            logger.debug(f"Message {message.message_id} enqueued to {queue_name}")
            return True
            
        except RedisError as e:
            logger.error(f"Redis error enqueueing message {message.message_id}: {e}")
            await self._circuit_breaker.record_failure()
            return False
        except Exception as e:
            logger.error(f"Unexpected error enqueueing message {message.message_id}: {e}")
            return False
    
    async def dequeue_message(self) -> Optional[TelegramMessage]:
        """
        Get next message from priority queues (CRITICAL -> HIGH -> NORMAL -> LOW)
        
        Returns:
            Next message to process or None if queues are empty
        """
        if not await self._circuit_breaker.call(self._is_redis_available):
            return None
        
        try:
            # Check queues in priority order
            for priority in [MessagePriority.CRITICAL, MessagePriority.HIGH, MessagePriority.NORMAL, MessagePriority.LOW]:
                queue_name = self.priority_queues[priority]
                
                # Get oldest message from this priority queue
                result = await self.redis_client.zpopmin(queue_name)
                
                if result:
                    message_data, _ = result[0]  # (message, score)
                    message = TelegramMessage.parse_raw(message_data)
                    
                    # Move to processing set
                    message.status = MessageStatus.PROCESSING
                    await self.redis_client.sadd(self.processing_set, message.json())
                    
                    # Update metrics
                    await self._decrement_metric("pending_messages")
                    await self._increment_metric("processing_messages")
                    
                    logger.debug(f"Dequeued message {message.message_id} from {queue_name}")
                    return message
            
            return None  # No messages in any queue
            
        except RedisError as e:
            logger.error(f"Redis error dequeuing message: {e}")
            await self._circuit_breaker.record_failure()
            return None
        except Exception as e:
            logger.error(f"Unexpected error dequeuing message: {e}")
            return None
    
    async def mark_message_sent(self, message: TelegramMessage) -> bool:
        """Mark message as successfully sent"""
        try:
            # Remove from processing set
            await self.redis_client.srem(self.processing_set, message.json())
            
            # Update metrics
            await self._decrement_metric("processing_messages")
            await self._increment_metric("total_processed")
            
            logger.debug(f"Message {message.message_id} marked as sent")
            return True
            
        except Exception as e:
            logger.error(f"Error marking message as sent: {e}")
            return False
    
    async def mark_message_failed(self, message: TelegramMessage, error: str) -> bool:
        """Mark message as failed and handle retry logic"""
        try:
            # Remove from processing set
            await self.redis_client.srem(self.processing_set, message.json())
            await self._decrement_metric("processing_messages")
            
            message.retry_count += 1
            message.error_message = error
            
            if message.retry_count <= message.max_retries:
                # Schedule retry with exponential backoff
                delay = self._calculate_retry_delay(message.retry_count)
                retry_time = datetime.utcnow() + timedelta(seconds=delay)
                message.scheduled_at = retry_time
                message.status = MessageStatus.RETRYING
                
                # Add to appropriate priority queue with future timestamp
                queue_name = self.priority_queues.get(message.priority, self.priority_queues[MessagePriority.NORMAL])
                await self.redis_client.zadd(queue_name, {message.json(): retry_time.timestamp()})
                
                await self._increment_metric("pending_messages")
                logger.info(f"Message {message.message_id} scheduled for retry #{message.retry_count} in {delay}s")
                
            else:
                # Move to dead letter queue
                await self.move_to_dlq(message, error)
                
            return True
            
        except Exception as e:
            logger.error(f"Error marking message as failed: {e}")
            return False
    
    async def move_to_dlq(self, message: TelegramMessage, error: str) -> bool:
        """Move message to dead letter queue"""
        try:
            dlq_entry = {
                "original_message": message.dict(),
                "error": error,
                "failed_at": datetime.utcnow().isoformat(),
                "retry_count": message.retry_count,
                "final_status": MessageStatus.DEAD_LETTER
            }
            
            await self.redis_client.lpush(self.dlq_name, json.dumps(dlq_entry))
            await self._increment_metric("dead_letter_messages")
            await self._increment_metric("failed_messages")
            
            logger.warning(f"Message {message.message_id} moved to DLQ after {message.retry_count} retries")
            return True
            
        except Exception as e:
            logger.error(f"Error moving message to DLQ: {e}")
            return False
    
    async def get_queue_metrics(self) -> QueueMetrics:
        """Get comprehensive queue metrics"""
        try:
            # Count messages in all priority queues
            pending_count = 0
            for queue_name in self.priority_queues.values():
                pending_count += await self.redis_client.zcard(queue_name)
            
            # Get other metrics
            processing_count = await self.redis_client.scard(self.processing_set)
            dlq_count = await self.redis_client.llen(self.dlq_name)
            
            # Get stored metrics
            metrics_data = await self.redis_client.hgetall(self.metrics_key)
            
            self._metrics.pending_messages = pending_count
            self._metrics.processing_messages = processing_count
            self._metrics.dead_letter_messages = dlq_count
            self._metrics.failed_messages = int(metrics_data.get("failed_messages", 0))
            self._metrics.total_processed = int(metrics_data.get("total_processed", 0))
            self._metrics.last_updated = datetime.utcnow()
            
            return self._metrics
            
        except Exception as e:
            logger.error(f"Error getting queue metrics: {e}")
            return self._metrics
    
    async def get_dlq_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get messages from dead letter queue"""
        try:
            dlq_messages = await self.redis_client.lrange(self.dlq_name, 0, limit - 1)
            return [json.loads(msg) for msg in dlq_messages]
            
        except Exception as e:
            logger.error(f"Error getting DLQ messages: {e}")
            return []
    
    async def requeue_dlq_message(self, dlq_index: int) -> bool:
        """Requeue a message from DLQ"""
        try:
            # Get message from DLQ
            dlq_entry_json = await self.redis_client.lindex(self.dlq_name, dlq_index)
            if not dlq_entry_json:
                return False
            
            dlq_entry = json.loads(dlq_entry_json)
            original_message = TelegramMessage(**dlq_entry["original_message"])
            
            # Reset retry count and status
            original_message.retry_count = 0
            original_message.status = MessageStatus.PENDING
            original_message.error_message = None
            
            # Requeue message
            success = await self.enqueue_message(original_message)
            
            if success:
                # Remove from DLQ
                await self.redis_client.lrem(self.dlq_name, 1, dlq_entry_json)
                await self._decrement_metric("dead_letter_messages")
                logger.info(f"Message {original_message.message_id} requeued from DLQ")
            
            return success
            
        except Exception as e:
            logger.error(f"Error requeuing DLQ message: {e}")
            return False
    
    async def clear_dlq(self) -> int:
        """Clear all messages from DLQ"""
        try:
            count = await self.redis_client.llen(self.dlq_name)
            await self.redis_client.delete(self.dlq_name)
            await self.redis_client.hset(self.metrics_key, "dead_letter_messages", 0)
            logger.info(f"Cleared {count} messages from DLQ")
            return count
            
        except Exception as e:
            logger.error(f"Error clearing DLQ: {e}")
            return 0
    
    def _calculate_retry_delay(self, retry_count: int) -> int:
        """Calculate exponential backoff delay"""
        base_delay = 60  # 1 minute base delay
        max_delay = 3600  # 1 hour max delay
        
        delay = min(base_delay * (self.settings.TELEGRAM_RETRY_BACKOFF_FACTOR ** (retry_count - 1)), max_delay)
        return int(delay)
    
    async def _is_redis_available(self) -> bool:
        """Check if Redis is available"""
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def _initialize_metrics(self):
        """Initialize metrics in Redis if they don't exist"""
        try:
            exists = await self.redis_client.exists(self.metrics_key)
            if not exists:
                initial_metrics = {
                    "total_processed": 0,
                    "failed_messages": 0,
                    "created_at": datetime.utcnow().isoformat()
                }
                await self.redis_client.hset(self.metrics_key, mapping=initial_metrics)
                
        except Exception as e:
            logger.error(f"Error initializing metrics: {e}")
    
    async def _increment_metric(self, metric_name: str, value: int = 1):
        """Increment a metric in Redis"""
        try:
            await self.redis_client.hincrby(self.metrics_key, metric_name, value)
        except Exception as e:
            logger.error(f"Error incrementing metric {metric_name}: {e}")
    
    async def _decrement_metric(self, metric_name: str, value: int = 1):
        """Decrement a metric in Redis"""
        try:
            await self.redis_client.hincrby(self.metrics_key, metric_name, -value)
        except Exception as e:
            logger.error(f"Error decrementing metric {metric_name}: {e}")


class CircuitBreaker:
    """Simple circuit breaker for Redis operations"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if datetime.utcnow().timestamp() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                return False
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self.record_success()
            return result
        except Exception:
            await self.record_failure()
            return False
    
    async def record_success(self):
        """Record successful operation"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    async def record_failure(self):
        """Record failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow().timestamp()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


# Global message queue instance
message_queue = TelegramMessageQueue()