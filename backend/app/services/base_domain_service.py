from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional
from sqlalchemy.orm import Session
from ..core.event_bus import EventBus, Event
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')  # Entity type
R = TypeVar('R')  # Repository type

class Result(Generic[T]):
    """Result wrapper for operations that can succeed or fail"""
    
    def __init__(self, success: bool, value: T = None, error: str = None):
        self.success = success
        self.value = value
        self.error = error
    
    @classmethod
    def success(cls, value: T) -> 'Result[T]':
        return cls(success=True, value=value)
    
    @classmethod
    def failure(cls, error: str) -> 'Result[T]':
        return cls(success=False, error=error)
    
    def is_success(self) -> bool:
        return self.success
    
    def is_failure(self) -> bool:
        return not self.success

class BaseDomainService(ABC, Generic[T, R]):
    """Base domain service with common functionality"""
    
    def __init__(self, db: Session, event_bus: EventBus):
        self.db = db
        self.event_bus = event_bus
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def _publish_event(self, event: Event):
        """Publish an event through the event bus"""
        try:
            await self.event_bus.publish(event)
        except Exception as e:
            self.logger.error(f"Failed to publish event {event.event_type}: {e}")
    
    def _commit_transaction(self):
        """Commit the current database transaction"""
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to commit transaction: {e}")
            raise
    
    def _rollback_transaction(self):
        """Rollback the current database transaction"""
        try:
            self.db.rollback()
        except Exception as e:
            self.logger.error(f"Failed to rollback transaction: {e}")
            raise