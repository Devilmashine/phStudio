from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
from ..models.booking_enhanced import Booking, BookingState
from ..services.booking_domain_service import BookingDomainService
from ..core.event_bus import EventBus
from ..core.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

class KanbanColumnType(Enum):
    """Kanban column types mapping to booking states"""
    NEW = "new"  # Draft/Pending bookings
    CONFIRMED = "confirmed"  # Confirmed bookings
    IN_PROGRESS = "in_progress"  # In progress bookings
    COMPLETED = "completed"  # Completed bookings
    CANCELLED = "cancelled"  # Cancelled bookings

@dataclass
class KanbanColumn:
    """Kanban column definition"""
    id: str
    title: str
    state: BookingState
    order: int
    color: str

@dataclass
class KanbanCard:
    """Kanban card representing a booking"""
    id: int
    reference: str
    title: str
    client_name: str
    start_time: datetime
    end_time: datetime
    state: BookingState
    column_id: str

class KanbanEngine:
    """Kanban board management engine"""
    
    # Default columns configuration
    DEFAULT_COLUMNS = [
        KanbanColumn(
            id=KanbanColumnType.NEW.value,
            title="New Bookings",
            state=BookingState.PENDING,
            order=1,
            color="#3B82F6"  # blue
        ),
        KanbanColumn(
            id=KanbanColumnType.CONFIRMED.value,
            title="Confirmed",
            state=BookingState.CONFIRMED,
            order=2,
            color="#10B981"  # green
        ),
        KanbanColumn(
            id=KanbanColumnType.IN_PROGRESS.value,
            title="In Progress",
            state=BookingState.IN_PROGRESS,
            order=3,
            color="#F59E0B"  # amber
        ),
        KanbanColumn(
            id=KanbanColumnType.COMPLETED.value,
            title="Completed",
            state=BookingState.COMPLETED,
            order=4,
            color="#6B7280"  # gray
        ),
        KanbanColumn(
            id=KanbanColumnType.CANCELLED.value,
            title="Cancelled",
            state=BookingState.CANCELLED,
            order=5,
            color="#EF4444"  # red
        ),
    ]
    
    def __init__(self, booking_service: BookingDomainService, event_bus: EventBus):
        self.booking_service = booking_service
        self.event_bus = event_bus
        self.ws_manager = ws_manager
        self.columns = {col.id: col for col in self.DEFAULT_COLUMNS}
    
    def get_columns(self) -> List[KanbanColumn]:
        """Get all kanban columns"""
        return list(self.columns.values())
    
    def get_column_by_state(self, state: BookingState) -> Optional[KanbanColumn]:
        """Get column by booking state"""
        for column in self.columns.values():
            if column.state == state:
                return column
        return None
    
    def get_cards_for_column(self, column_id: str) -> List[KanbanCard]:
        """Get all cards for a specific column"""
        column = self.columns.get(column_id)
        if not column:
            return []
        
        # Get bookings with the column's state
        result = self.booking_service.get_bookings_by_state(column.state)
        if result.is_failure():
            logger.error(f"Failed to get bookings for state {column.state}: {result.error}")
            return []
        
        bookings = result.value
        cards = []
        
        for booking in bookings:
            card = KanbanCard(
                id=booking.id,
                reference=booking.booking_reference,
                title=f"{booking.space_type} - {booking.duration_hours}h",
                client_name=booking.client_name,
                start_time=booking.start_time,
                end_time=booking.end_time,
                state=booking.state,
                column_id=column_id
            )
            cards.append(card)
        
        return cards
    
    def get_all_cards(self) -> Dict[str, List[KanbanCard]]:
        """Get all cards organized by column"""
        cards_by_column = {}
        for column_id in self.columns:
            cards_by_column[column_id] = self.get_cards_for_column(column_id)
        return cards_by_column
    
    async def move_card(
        self,
        card_id: int,
        to_column_id: str,
        employee_id: int = None
    ) -> bool:
        """Move a card from one column to another by changing booking state"""
        # Validate target column exists
        target_column = self.columns.get(to_column_id)
        if not target_column:
            logger.error(f"Target column {to_column_id} not found")
            return False
        
        # Get current column for the booking
        booking_result = self.booking_service.get_by_id(card_id)
        if booking_result.is_failure() or not booking_result.value:
            logger.error(f"Booking {card_id} not found")
            return False
        
        current_booking = booking_result.value
        current_column = self.get_column_by_state(current_booking.state)
        
        # Transition booking state
        result = await self.booking_service.transition_state(
            booking_id=card_id,
            target_state=target_column.state,
            employee_id=employee_id
        )
        
        if result.is_failure():
            logger.error(f"Failed to transition booking {card_id}: {result.error}")
            return False
        
        # Create and publish event for real-time updates
        # event = create_event(
        #     event_type="kanban_card_moved",
        #     payload={
        #         "card_id": card_id,
        #         "from_column_id": current_column.id if current_column else None,
        #         "to_column_id": to_column_id,
        #         "employee_id": employee_id,
        #         "timestamp": datetime.now().isoformat()
        #     }
        # )
        # await self.event_bus.publish(event)
        
        # Broadcast update via WebSocket
        try:
            await self.ws_manager.broadcast_to_room(
                room="kanban_board",
                message={
                    "type": "card_moved",
                    "card_id": card_id,
                    "from_column_id": current_column.id if current_column else None,
                    "to_column_id": to_column_id,
                    "employee_id": employee_id
                }
            )
        except Exception as e:
            logger.error(f"Failed to broadcast WebSocket update: {e}")
        
        logger.info(f"Moved card {card_id} from column {current_column.id if current_column else 'unknown'} to column {to_column_id}")
        return True