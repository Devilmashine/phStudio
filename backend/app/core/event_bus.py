from typing import Dict, List, Callable, Any, TypeVar, Generic
import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Type variables for generic event handling
T = TypeVar('T')

@dataclass
class Event:
    """Base event class"""
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = None

class EventBus:
    """Simple in-memory event bus implementation"""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._middleware: List[Callable] = []
    
    def add_middleware(self, middleware: Callable):
        """Add middleware to process events before handling"""
        self._middleware.append(middleware)
    
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe a handler to an event type"""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(f"Subscribed handler to event type: {event_type}")
    
    async def publish(self, event: Event):
        """Publish an event to all subscribed handlers"""
        logger.info(f"Publishing event: {event.event_type}")
        
        # Apply middleware
        for middleware in self._middleware:
            try:
                await middleware(event)
            except Exception as e:
                logger.error(f"Error in middleware: {e}")
        
        # Get handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        
        # Execute all handlers concurrently
        if handlers:
            tasks = []
            for handler in handlers:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(event))
                    else:
                        # Run sync handlers in thread pool
                        tasks.append(asyncio.get_event_loop().run_in_executor(None, handler, event))
                except Exception as e:
                    logger.error(f"Error preparing handler for event {event.event_type}: {e}")
            
            if tasks:
                try:
                    await asyncio.gather(*tasks, return_exceptions=True)
                except Exception as e:
                    logger.error(f"Error executing handlers for event {event.event_type}: {e}")
        else:
            logger.debug(f"No handlers found for event type: {event.event_type}")

# Global event bus instance
event_bus = EventBus()

# Helper function to create events
def create_event(event_type: str, payload: Dict[str, Any], metadata: Dict[str, Any] = None) -> Event:
    """Create a new event"""
    return Event(
        event_type=event_type,
        timestamp=datetime.now(),
        payload=payload,
        metadata=metadata or {}
    )