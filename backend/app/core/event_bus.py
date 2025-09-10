"""
Event Bus implementation for domain-driven design architecture.

This module provides a lightweight event bus for loose coupling between
components without external message queue dependencies.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union
from uuid import UUID, uuid4

import structlog

logger = structlog.get_logger(__name__)


class EventType(str, Enum):
    """Standard event types for the system."""
    BOOKING_CREATED = "booking.created"
    BOOKING_UPDATED = "booking.updated"
    BOOKING_STATE_CHANGED = "booking.state_changed"
    BOOKING_CANCELLED = "booking.cancelled"
    EMPLOYEE_LOGIN = "employee.login"
    EMPLOYEE_LOGOUT = "employee.logout"
    AUDIT_LOG_CREATED = "audit_log.created"
    CACHE_INVALIDATED = "cache.invalidated"


@dataclass
class EventMetadata:
    """Metadata for domain events."""
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


@dataclass
class DomainEvent(ABC):
    """Base class for all domain events."""
    metadata: EventMetadata = field(default_factory=EventMetadata)
    
    @property
    @abstractmethod
    def event_type(self) -> EventType:
        """Return the type of this event."""
        pass
    
    @property
    @abstractmethod
    def aggregate_id(self) -> str:
        """Return the ID of the aggregate that generated this event."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type.value,
            "aggregate_id": self.aggregate_id,
            "metadata": {
                "event_id": str(self.metadata.event_id),
                "occurred_at": self.metadata.occurred_at.isoformat(),
                "correlation_id": self.metadata.correlation_id,
                "causation_id": self.metadata.causation_id,
                "user_id": self.metadata.user_id,
                "session_id": self.metadata.session_id,
                "ip_address": self.metadata.ip_address,
                "user_agent": self.metadata.user_agent,
            }
        }


class EventHandler(ABC):
    """Base class for event handlers."""
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle the given domain event."""
        pass


class EventBus(ABC):
    """Abstract event bus interface."""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to events of a specific type."""
        pass
    
    @abstractmethod
    async def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe from events of a specific type."""
        pass


class InMemoryEventBus(EventBus):
    """
    In-memory event bus implementation.
    
    This is suitable for single-instance deployments and development.
    For production multi-instance deployments, consider using Redis pub/sub.
    """
    
    def __init__(self):
        self._handlers: Dict[EventType, Set[EventHandler]] = {}
        self._event_history: List[DomainEvent] = []
        self._max_history_size = 1000
        self._lock = asyncio.Lock()
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        async with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history_size:
                self._event_history.pop(0)
            
            # Get handlers for this event type
            handlers = self._handlers.get(event.event_type, set()).copy()
        
        # Execute handlers asynchronously
        if handlers:
            tasks = [handler.handle(event) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info(
                "Event published",
                event_type=event.event_type.value,
                aggregate_id=event.aggregate_id,
                handler_count=len(handlers)
            )
        else:
            logger.debug(
                "Event published but no handlers registered",
                event_type=event.event_type.value,
                aggregate_id=event.aggregate_id
            )
    
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to events of a specific type."""
        async with self._lock:
            if event_type not in self._handlers:
                self._handlers[event_type] = set()
            self._handlers[event_type].add(handler)
            
            logger.info(
                "Handler subscribed",
                event_type=event_type.value,
                handler_type=type(handler).__name__
            )
    
    async def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe from events of a specific type."""
        async with self._lock:
            if event_type in self._handlers:
                self._handlers[event_type].discard(handler)
                if not self._handlers[event_type]:
                    del self._handlers[event_type]
                
                logger.info(
                    "Handler unsubscribed",
                    event_type=event_type.value,
                    handler_type=type(handler).__name__
                )
    
    def get_event_history(self, limit: Optional[int] = None) -> List[DomainEvent]:
        """Get recent event history for debugging and auditing."""
        if limit is None:
            return self._event_history.copy()
        return self._event_history[-limit:]
    
    def clear_history(self) -> None:
        """Clear event history (useful for testing)."""
        self._event_history.clear()


class RedisEventBus(EventBus):
    """
    Redis-based event bus for distributed deployments.
    
    This implementation uses Redis pub/sub for cross-instance communication.
    """
    
    def __init__(self, redis_client, channel_prefix: str = "events"):
        self.redis = redis_client
        self.channel_prefix = channel_prefix
        self._local_handlers: Dict[EventType, Set[EventHandler]] = {}
        self._pubsub = None
        self._lock = asyncio.Lock()
    
    async def start(self) -> None:
        """Start the Redis event bus."""
        self._pubsub = self.redis.pubsub()
        await self._pubsub.subscribe(f"{self.channel_prefix}:*")
        
        # Start background task to process messages
        asyncio.create_task(self._process_messages())
        
        logger.info("Redis event bus started")
    
    async def stop(self) -> None:
        """Stop the Redis event bus."""
        if self._pubsub:
            await self._pubsub.unsubscribe()
            await self._pubsub.close()
            logger.info("Redis event bus stopped")
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to Redis and local handlers."""
        # Publish to Redis for other instances
        channel = f"{self.channel_prefix}:{event.event_type.value}"
        await self.redis.publish(channel, event.to_dict())
        
        # Handle locally
        await self._handle_local(event)
        
        logger.info(
            "Event published to Redis",
            event_type=event.event_type.value,
            aggregate_id=event.aggregate_id,
            channel=channel
        )
    
    async def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Subscribe to events of a specific type."""
        async with self._lock:
            if event_type not in self._local_handlers:
                self._local_handlers[event_type] = set()
            self._local_handlers[event_type].add(handler)
    
    async def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """Unsubscribe from events of a specific type."""
        async with self._lock:
            if event_type in self._local_handlers:
                self._local_handlers[event_type].discard(handler)
    
    async def _handle_local(self, event: DomainEvent) -> None:
        """Handle event with local handlers."""
        handlers = self._local_handlers.get(event.event_type, set()).copy()
        if handlers:
            tasks = [handler.handle(event) for handler in handlers]
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _process_messages(self) -> None:
        """Process messages from Redis pub/sub."""
        try:
            async for message in self._pubsub.listen():
                if message["type"] == "message":
                    event_data = message["data"]
                    # Reconstruct event from data
                    # This is a simplified version - in production you'd want proper deserialization
                    await self._handle_local(event_data)
        except Exception as e:
            logger.error("Error processing Redis messages", error=str(e))


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = InMemoryEventBus()
        logger.info("In-memory event bus initialized")
    return _event_bus


def set_event_bus(event_bus: EventBus) -> None:
    """Set the global event bus instance."""
    global _event_bus
    _event_bus = event_bus
    logger.info(f"Event bus set to {type(event_bus).__name__}")


# Convenience functions for common operations
async def publish_event(event: DomainEvent) -> None:
    """Publish an event using the global event bus."""
    event_bus = get_event_bus()
    await event_bus.publish(event)


async def subscribe_to_events(event_types: List[EventType], handler: EventHandler) -> None:
    """Subscribe to multiple event types."""
    event_bus = get_event_bus()
    for event_type in event_types:
        await event_bus.subscribe(event_type, handler)


# Example event implementations
@dataclass
class BookingCreatedEvent(DomainEvent):
    """Event emitted when a booking is created."""
    booking_id: int = 0
    reference: str = ""
    client_name: str = ""
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    @property
    def event_type(self) -> EventType:
        return EventType.BOOKING_CREATED
    
    @property
    def aggregate_id(self) -> str:
        return f"booking:{self.booking_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "booking_id": self.booking_id,
            "reference": self.reference,
            "client_name": self.client_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
        })
        return base_dict


@dataclass
class BookingStateChangedEvent(DomainEvent):
    """Event emitted when a booking state changes."""
    booking_id: int = 0
    from_state: str = ""
    to_state: str = ""
    changed_by: int = 0
    
    @property
    def event_type(self) -> EventType:
        return EventType.BOOKING_STATE_CHANGED
    
    @property
    def aggregate_id(self) -> str:
        return f"booking:{self.booking_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "booking_id": self.booking_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "changed_by": self.changed_by,
        })
        return base_dict


# Example handler implementation
class LoggingEventHandler(EventHandler):
    """Example event handler that logs all events."""
    
    async def handle(self, event: DomainEvent) -> None:
        logger.info(
            "Event handled",
            event_type=event.event_type.value,
            aggregate_id=event.aggregate_id,
            metadata=event.metadata
        )


# Initialize default handlers
async def initialize_default_handlers() -> None:
    """Initialize default event handlers."""
    event_bus = get_event_bus()
    logging_handler = LoggingEventHandler()
    
    # Subscribe to all event types
    for event_type in EventType:
        await event_bus.subscribe(event_type, logging_handler)
    
    logger.info("Default event handlers initialized")