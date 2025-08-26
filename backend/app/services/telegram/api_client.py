"""
Telegram Bot API Client

Enterprise-grade HTTP client for Telegram Bot API with features:
- Connection pooling and reuse
- Rate limiting with token bucket algorithm
- Circuit breaker pattern for resilience
- Comprehensive error handling and retries
- Request/response logging and metrics
- Webhook management
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp.client_exceptions import ClientError
from aiohttp import ClientTimeout as AioTimeout

from app.core.config import get_settings
from app.models.telegram import (
    TelegramMessage,
    MessageResult,
    BotInfo,
    TelegramAPIError,
    TelegramConfigError
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for Telegram API requests"""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.bucket_size = requests_per_minute
        self.tokens = requests_per_minute
        self.last_update = datetime.utcnow()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> bool:
        """Acquire a token for making a request"""
        async with self._lock:
            now = datetime.utcnow()
            time_passed = (now - self.last_update).total_seconds()
            
            # Add tokens based on time passed
            tokens_to_add = time_passed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.bucket_size, self.tokens + tokens_to_add)
            self.last_update = now
            
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
    
    async def wait_for_token(self) -> None:
        """Wait until a token is available"""
        while not await self.acquire():
            await asyncio.sleep(0.1)


class TelegramAPIClient:
    """
    Robust Telegram Bot API client with enterprise features:
    - Connection pooling for performance
    - Rate limiting to respect API limits
    - Circuit breaker for fault tolerance
    - Comprehensive error handling
    - Request/response metrics
    """
    
    def __init__(self):
        self.settings = get_settings()
        
        if not self.settings.validate_telegram_config():
            raise TelegramConfigError("Invalid Telegram configuration")
        
        self.bot_token = self.settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # HTTP client configuration
        self.timeout = ClientTimeout(total=self.settings.TELEGRAM_API_TIMEOUT)
        self.connector = TCPConnector(
            limit=self.settings.TELEGRAM_CONNECTION_POOL_SIZE,
            limit_per_host=self.settings.TELEGRAM_CONNECTION_POOL_SIZE,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.session: Optional[ClientSession] = None
        self.rate_limiter = RateLimiter(self.settings.TELEGRAM_RATE_LIMIT_REQUESTS)
        self._circuit_breaker = APICircuitBreaker()
        
        # Metrics
        self.request_count = 0
        self.error_count = 0
        self.last_request_time = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def initialize(self):
        """Initialize the HTTP client session"""
        if self.session is None:
            self.session = ClientSession(
                timeout=self.timeout,
                connector=self.connector,
                headers={
                    'User-Agent': 'phStudio-TelegramBot/2.0',
                    'Content-Type': 'application/json'
                }
            )
            logger.info("Telegram API client initialized")
    
    async def close(self):
        """Close the HTTP client session"""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("Telegram API client closed")
    
    async def send_message(self, message: TelegramMessage) -> MessageResult:
        """
        Send a message via Telegram Bot API
        
        Args:
            message: Telegram message to send
            
        Returns:
            MessageResult with send status and details
        """
        if not self.session:
            await self.initialize()
        
        try:
            # Rate limiting
            await self.rate_limiter.wait_for_token()
            
            # Circuit breaker check
            if not await self._circuit_breaker.can_proceed():
                error_msg = "Circuit breaker is open"
                logger.warning(error_msg)
                return MessageResult(
                    success=False,
                    error=error_msg
                )
            
            # Prepare request payload
            payload = {
                "chat_id": message.chat_id,
                "text": message.text,
                "parse_mode": message.parse_mode
            }
            
            if message.reply_markup:
                payload["reply_markup"] = message.reply_markup
            
            # Make API request
            url = f"{self.base_url}/sendMessage"
            start_time = datetime.utcnow()
            
            async with self.session.post(url, json=payload) as response:
                response_data = await response.json()
                
                # Update metrics
                self.request_count += 1
                self.last_request_time = datetime.utcnow()
                
                if response.status == 200 and response_data.get("ok"):
                    # Success
                    result = response_data.get("result", {})
                    telegram_message_id = result.get("message_id")
                    
                    await self._circuit_breaker.record_success()
                    
                    logger.debug(f"Successfully sent message {message.message_id}")
                    return MessageResult(
                        success=True,
                        message_id=message.message_id,
                        telegram_message_id=telegram_message_id,
                        sent_at=datetime.utcnow()
                    )
                
                else:
                    # API error
                    error_code = response_data.get("error_code", response.status)
                    error_description = response_data.get("description", "Unknown error")
                    
                    self.error_count += 1
                    await self._circuit_breaker.record_failure()
                    
                    # Handle specific error codes
                    if error_code == 429:  # Too Many Requests
                        retry_after = response_data.get("parameters", {}).get("retry_after", 60)
                        logger.warning(f"Rate limited, retry after {retry_after} seconds")
                        return MessageResult(
                            success=False,
                            error=f"Rate limited: {error_description}",
                            retry_after=retry_after
                        )
                    
                    elif error_code in [400, 403]:  # Bad Request or Forbidden
                        logger.error(f"Permanent error {error_code}: {error_description}")
                        return MessageResult(
                            success=False,
                            error=f"Permanent error: {error_description}"
                        )
                    
                    else:  # Temporary error
                        logger.warning(f"Temporary error {error_code}: {error_description}")
                        return MessageResult(
                            success=False,
                            error=f"Temporary error: {error_description}"
                        )
        
        except AioTimeout:
            error_msg = "Request timeout"
            logger.error(f"Timeout sending message {message.message_id}")
            self.error_count += 1
            await self._circuit_breaker.record_failure()
            return MessageResult(success=False, error=error_msg)
        
        except ClientError as e:
            error_msg = f"HTTP client error: {str(e)}"
            logger.error(f"Client error sending message {message.message_id}: {e}")
            self.error_count += 1
            await self._circuit_breaker.record_failure()
            return MessageResult(success=False, error=error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Unexpected error sending message {message.message_id}: {e}")
            self.error_count += 1
            await self._circuit_breaker.record_failure()
            return MessageResult(success=False, error=error_msg)
    
    async def send_message_batch(self, messages: List[TelegramMessage]) -> List[MessageResult]:
        """
        Send multiple messages with concurrency control
        
        Args:
            messages: List of messages to send
            
        Returns:
            List of MessageResult objects
        """
        if not messages:
            return []
        
        # Limit concurrency to avoid overwhelming the API
        semaphore = asyncio.Semaphore(5)
        
        async def send_with_semaphore(msg):
            async with semaphore:
                return await self.send_message(msg)
        
        tasks = [send_with_semaphore(msg) for msg in messages]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(MessageResult(
                    success=False,
                    error=f"Exception: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def get_bot_info(self) -> BotInfo:
        """
        Get information about the bot
        
        Returns:
            BotInfo object with bot details
        """
        if not self.session:
            await self.initialize()
        
        try:
            await self.rate_limiter.wait_for_token()
            
            url = f"{self.base_url}/getMe"
            
            async with self.session.get(url) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("ok"):
                    bot_data = response_data.get("result", {})
                    return BotInfo(**bot_data)
                else:
                    error_msg = response_data.get("description", "Failed to get bot info")
                    raise TelegramAPIError(error_msg, response.status, response_data)
        
        except Exception as e:
            logger.error(f"Error getting bot info: {e}")
            raise TelegramAPIError(f"Failed to get bot info: {str(e)}")
    
    async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> bool:
        """
        Set webhook URL for the bot
        
        Args:
            url: Webhook URL
            secret_token: Secret token for webhook validation
            
        Returns:
            True if webhook was set successfully
        """
        if not self.session:
            await self.initialize()
        
        try:
            await self.rate_limiter.wait_for_token()
            
            payload = {
                "url": url,
                "allowed_updates": ["message", "callback_query"]
            }
            
            if secret_token:
                payload["secret_token"] = secret_token
            
            api_url = f"{self.base_url}/setWebhook"
            
            async with self.session.post(api_url, json=payload) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("ok"):
                    logger.info(f"Webhook set successfully: {url}")
                    return True
                else:
                    error_msg = response_data.get("description", "Failed to set webhook")
                    logger.error(f"Failed to set webhook: {error_msg}")
                    return False
        
        except Exception as e:
            logger.error(f"Error setting webhook: {e}")
            return False
    
    async def delete_webhook(self) -> bool:
        """
        Delete webhook for the bot
        
        Returns:
            True if webhook was deleted successfully
        """
        if not self.session:
            await self.initialize()
        
        try:
            await self.rate_limiter.wait_for_token()
            
            url = f"{self.base_url}/deleteWebhook"
            
            async with self.session.post(url) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("ok"):
                    logger.info("Webhook deleted successfully")
                    return True
                else:
                    error_msg = response_data.get("description", "Failed to delete webhook")
                    logger.error(f"Failed to delete webhook: {error_msg}")
                    return False
        
        except Exception as e:
            logger.error(f"Error deleting webhook: {e}")
            return False
    
    async def get_webhook_info(self) -> Dict[str, Any]:
        """Get current webhook information"""
        if not self.session:
            await self.initialize()
        
        try:
            await self.rate_limiter.wait_for_token()
            
            url = f"{self.base_url}/getWebhookInfo"
            
            async with self.session.get(url) as response:
                response_data = await response.json()
                
                if response.status == 200 and response_data.get("ok"):
                    return response_data.get("result", {})
                else:
                    return {}
        
        except Exception as e:
            logger.error(f"Error getting webhook info: {e}")
            return {}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get client metrics"""
        return {
            "request_count": self.request_count,
            "error_count": self.error_count,
            "error_rate": self.error_count / max(self.request_count, 1),
            "last_request_time": self.last_request_time.isoformat() if self.last_request_time else None,
            "circuit_breaker_state": self._circuit_breaker.state,
            "rate_limiter_tokens": self.rate_limiter.tokens
        }


class APICircuitBreaker:
    """Circuit breaker for API calls"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def can_proceed(self) -> bool:
        """Check if requests can proceed"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if datetime.utcnow().timestamp() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    async def record_success(self):
        """Record successful API call"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    async def record_failure(self):
        """Record failed API call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow().timestamp()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")


# Global API client instance
api_client = TelegramAPIClient()