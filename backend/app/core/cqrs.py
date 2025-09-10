"""
CQRS (Command Query Responsibility Segregation) implementation.

This module provides the foundation for separating command and query
responsibilities in the domain services.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Callable
from datetime import datetime

from .result import Result, success, failure, DomainError

T = TypeVar('T')


class Command(ABC):
    """Base class for all commands."""
    
    @property
    @abstractmethod
    def command_type(self) -> str:
        """Return the type of this command."""
        pass
    
    @property
    @abstractmethod
    def aggregate_id(self) -> str:
        """Return the ID of the aggregate this command operates on."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert command to dictionary for serialization."""
        return {
            "command_type": self.command_type,
            "aggregate_id": self.aggregate_id,
            "timestamp": datetime.utcnow().isoformat()
        }


class Query(ABC):
    """Base class for all queries."""
    
    @property
    @abstractmethod
    def query_type(self) -> str:
        """Return the type of this query."""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert query to dictionary for serialization."""
        return {
            "query_type": self.query_type,
            "timestamp": datetime.utcnow().isoformat()
        }


class CommandHandler(ABC, Generic[T]):
    """Base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: Command) -> Result[T, DomainError]:
        """Handle the given command."""
        pass


class QueryHandler(ABC, Generic[T]):
    """Base class for query handlers."""
    
    @abstractmethod
    async def handle(self, query: Query) -> Result[T, DomainError]:
        """Handle the given query."""
        pass


class CommandBus(ABC):
    """Abstract command bus interface."""
    
    @abstractmethod
    async def execute(self, command: Command) -> Result[Any, DomainError]:
        """Execute a command."""
        pass
    
    @abstractmethod
    def register_handler(self, command_type: str, handler: CommandHandler) -> None:
        """Register a handler for a specific command type."""
        pass


class QueryBus(ABC):
    """Abstract query bus interface."""
    
    @abstractmethod
    async def execute(self, query: Query) -> Result[Any, DomainError]:
        """Execute a query."""
        pass
    
    @abstractmethod
    def register_handler(self, query_type: str, handler: QueryHandler) -> None:
        """Register a handler for a specific query type."""
        pass


class InMemoryCommandBus(CommandBus):
    """In-memory command bus implementation."""
    
    def __init__(self):
        self._handlers: Dict[str, CommandHandler] = {}
    
    def register_handler(self, command_type: str, handler: CommandHandler) -> None:
        """Register a handler for a specific command type."""
        self._handlers[command_type] = handler
    
    async def execute(self, command: Command) -> Result[Any, DomainError]:
        """Execute a command using the registered handler."""
        command_type = command.command_type
        
        if command_type not in self._handlers:
            return failure(
                DomainError(
                    f"No handler registered for command type: {command_type}",
                    code="HANDLER_NOT_FOUND"
                )
            )
        
        try:
            handler = self._handlers[command_type]
            return await handler.handle(command)
        except Exception as e:
            return failure(
                DomainError(
                    f"Error executing command {command_type}: {str(e)}",
                    code="COMMAND_EXECUTION_ERROR"
                )
            )


class InMemoryQueryBus(QueryBus):
    """In-memory query bus implementation."""
    
    def __init__(self):
        self._handlers: Dict[str, QueryHandler] = {}
    
    def register_handler(self, query_type: str, handler: QueryHandler) -> None:
        """Register a handler for a specific query type."""
        self._handlers[query_type] = handler
    
    async def execute(self, query: Query) -> Result[Any, DomainError]:
        """Execute a query using the registered handler."""
        query_type = query.query_type
        
        if query_type not in self._handlers:
            return failure(
                DomainError(
                    f"No handler registered for query type: {query_type}",
                    code="HANDLER_NOT_FOUND"
                )
            )
        
        try:
            handler = self._handlers[query_type]
            return await handler.handle(query)
        except Exception as e:
            return failure(
                DomainError(
                    f"Error executing query {query_type}: {str(e)}",
                    code="QUERY_EXECUTION_ERROR"
                )
            )


# Global bus instances
_command_bus: Optional[CommandBus] = None
_query_bus: Optional[QueryBus] = None


def get_command_bus() -> CommandBus:
    """Get the global command bus instance."""
    global _command_bus
    if _command_bus is None:
        _command_bus = InMemoryCommandBus()
    return _command_bus


def get_query_bus() -> QueryBus:
    """Get the global query bus instance."""
    global _query_bus
    if _query_bus is None:
        _query_bus = InMemoryQueryBus()
    return _query_bus


def set_command_bus(command_bus: CommandBus) -> None:
    """Set the global command bus instance."""
    global _command_bus
    _command_bus = command_bus


def set_query_bus(query_bus: QueryBus) -> None:
    """Set the global query bus instance."""
    global _query_bus
    _query_bus = query_bus


# Convenience functions
async def execute_command(command: Command) -> Result[Any, DomainError]:
    """Execute a command using the global command bus."""
    command_bus = get_command_bus()
    return await command_bus.execute(command)


async def execute_query(query: Query) -> Result[Any, DomainError]:
    """Execute a query using the global query bus."""
    query_bus = get_query_bus()
    return await query_bus.execute(query)


# Example command implementations
@dataclass
class CreateBookingCommand(Command):
    """Command to create a new booking."""
    client_name: str
    client_phone: str
    client_email: Optional[str]
    start_time: datetime
    end_time: datetime
    space_type: str
    equipment_requested: Dict[str, Any]
    special_requirements: Optional[str]
    notes: Optional[str]
    
    @property
    def command_type(self) -> str:
        return "create_booking"
    
    @property
    def aggregate_id(self) -> str:
        # For new bookings, we don't have an ID yet
        return "new_booking"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_email": self.client_email,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "space_type": self.space_type,
            "equipment_requested": self.equipment_requested,
            "special_requirements": self.special_requirements,
            "notes": self.notes,
        })
        return base_dict


@dataclass
class UpdateBookingCommand(Command):
    """Command to update an existing booking."""
    booking_id: int
    client_name: Optional[str] = None
    client_phone: Optional[str] = None
    client_email: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    space_type: Optional[str] = None
    equipment_requested: Optional[Dict[str, Any]] = None
    special_requirements: Optional[str] = None
    notes: Optional[str] = None
    
    @property
    def command_type(self) -> str:
        return "update_booking"
    
    @property
    def aggregate_id(self) -> str:
        return f"booking:{self.booking_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "booking_id": self.booking_id,
            "client_name": self.client_name,
            "client_phone": self.client_phone,
            "client_email": self.client_email,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "space_type": self.space_type,
            "equipment_requested": self.equipment_requested,
            "special_requirements": self.special_requirements,
            "notes": self.notes,
        })
        return base_dict


@dataclass
class CancelBookingCommand(Command):
    """Command to cancel a booking."""
    booking_id: int
    reason: Optional[str] = None
    cancelled_by: Optional[int] = None
    
    @property
    def command_type(self) -> str:
        return "cancel_booking"
    
    @property
    def aggregate_id(self) -> str:
        return f"booking:{self.booking_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "booking_id": self.booking_id,
            "reason": self.reason,
            "cancelled_by": self.cancelled_by,
        })
        return base_dict


@dataclass
class TransitionBookingStateCommand(Command):
    """Command to transition booking to a new state."""
    booking_id: int
    target_state: str
    transitioned_by: int
    reason: Optional[str] = None
    
    @property
    def command_type(self) -> str:
        return "transition_booking_state"
    
    @property
    def aggregate_id(self) -> str:
        return f"booking:{self.booking_id}"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "booking_id": self.booking_id,
            "target_state": self.target_state,
            "transitioned_by": self.transitioned_by,
            "reason": self.reason,
        })
        return base_dict


# Example query implementations
@dataclass
class GetBookingQuery(Query):
    """Query to get a specific booking."""
    booking_id: int
    
    @property
    def query_type(self) -> str:
        return "get_booking"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "booking_id": self.booking_id,
        })
        return base_dict


@dataclass
class GetBookingsForDateQuery(Query):
    """Query to get bookings for a specific date."""
    date: datetime
    filters: Optional[Dict[str, Any]] = None
    
    @property
    def query_type(self) -> str:
        return "get_bookings_for_date"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "date": self.date.isoformat(),
            "filters": self.filters,
        })
        return base_dict


@dataclass
class GetBookingAnalyticsQuery(Query):
    """Query to get booking analytics."""
    start_date: datetime
    end_date: datetime
    group_by: Optional[str] = None
    
    @property
    def query_type(self) -> str:
        return "get_booking_analytics"
    
    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        base_dict.update({
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "group_by": self.group_by,
        })
        return base_dict


# Example handler implementations
class CreateBookingCommandHandler(CommandHandler[Dict[str, Any]]):
    """Handler for creating bookings."""
    
    def __init__(self, booking_service):
        self.booking_service = booking_service
    
    async def handle(self, command: CreateBookingCommand) -> Result[Dict[str, Any], DomainError]:
        """Handle create booking command."""
        try:
            # Delegate to domain service
            result = await self.booking_service.create_booking(command)
            return result
        except Exception as e:
            return failure(
                DomainError(
                    f"Failed to create booking: {str(e)}",
                    code="BOOKING_CREATION_FAILED"
                )
            )


class GetBookingQueryHandler(QueryHandler[Dict[str, Any]]):
    """Handler for getting bookings."""
    
    def __init__(self, booking_service):
        self.booking_service = booking_service
    
    async def handle(self, query: GetBookingQuery) -> Result[Dict[str, Any], DomainError]:
        """Handle get booking query."""
        try:
            # Delegate to domain service
            result = await self.booking_service.get_booking(query.booking_id)
            return result
        except Exception as e:
            return failure(
                DomainError(
                    f"Failed to get booking: {str(e)}",
                    code="BOOKING_RETRIEVAL_FAILED"
                )
            )


# Registration helpers
def register_booking_handlers(
    command_bus: CommandBus,
    query_bus: QueryBus,
    booking_service
) -> None:
    """Register all booking-related handlers."""
    
    # Command handlers
    command_bus.register_handler(
        "create_booking",
        CreateBookingCommandHandler(booking_service)
    )
    
    # Query handlers
    query_bus.register_handler(
        "get_booking",
        GetBookingQueryHandler(booking_service)
    )


# Middleware support
class CommandMiddleware(ABC):
    """Base class for command middleware."""
    
    @abstractmethod
    async def process(self, command: Command, next_handler: Callable) -> Result[Any, DomainError]:
        """Process the command through this middleware."""
        pass


class QueryMiddleware(ABC):
    """Base class for query middleware."""
    
    @abstractmethod
    async def process(self, query: Query, next_handler: Callable) -> Result[Any, DomainError]:
        """Process the query through this middleware."""
        pass


class LoggingCommandMiddleware(CommandMiddleware):
    """Middleware that logs all commands."""
    
    async def process(self, command: Command, next_handler: Callable) -> Result[Any, DomainError]:
        # Log command
        print(f"Executing command: {command.command_type}")
        
        # Execute next handler
        result = await next_handler(command)
        
        # Log result
        if result.is_success():
            print(f"Command {command.command_type} executed successfully")
        else:
            print(f"Command {command.command_type} failed: {result.error()}")
        
        return result


class ValidationCommandMiddleware(CommandMiddleware):
    """Middleware that validates commands."""
    
    async def process(self, command: Command, next_handler: Callable) -> Result[Any, DomainError]:
        # Validate command
        validation_result = self._validate_command(command)
        if validation_result.is_failure():
            return validation_result
        
        # Execute next handler
        return await next_handler(command)
    
    def _validate_command(self, command: Command) -> Result[None, DomainError]:
        """Validate the command."""
        # Basic validation - override in subclasses
        return success(None)