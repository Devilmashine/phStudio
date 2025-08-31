from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel
import logging

from ...core.database import get_db
from ...services.kanban_service import KanbanEngine, KanbanColumn, KanbanCard
from ...services.booking_domain_service import BookingDomainService
from ...core.event_bus import event_bus
from ...repositories.booking_repository import BookingRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kanban", tags=["kanban"])

# Pydantic models for API
class KanbanColumnResponse(BaseModel):
    id: str
    title: str
    order: int
    color: str

class KanbanCardResponse(BaseModel):
    id: int
    reference: str
    title: str
    client_name: str
    start_time: str
    end_time: str
    state: str
    column_id: str

class KanbanBoardResponse(BaseModel):
    columns: List[KanbanColumnResponse]
    cards: Dict[str, List[KanbanCardResponse]]

class MoveCardRequest(BaseModel):
    to_column_id: str
    employee_id: int

# Helper functions to convert domain models to responses
def column_to_response(column: KanbanColumn) -> KanbanColumnResponse:
    return KanbanColumnResponse(
        id=column.id,
        title=column.title,
        order=column.order,
        color=column.color
    )

def card_to_response(card: KanbanCard) -> KanbanCardResponse:
    return KanbanCardResponse(
        id=card.id,
        reference=card.reference,
        title=card.title,
        client_name=card.client_name,
        start_time=card.start_time.isoformat() if card.start_time else None,
        end_time=card.end_time.isoformat() if card.end_time else None,
        state=card.state.value if card.state else None,
        column_id=card.column_id
    )

@router.get("/board", response_model=KanbanBoardResponse)
async def get_kanban_board(
    db: Session = Depends(get_db)
):
    """Get the complete Kanban board with columns and cards"""
    try:
        # Initialize services
        booking_repo = BookingRepository(db)
        booking_service = BookingDomainService(db, event_bus)
        kanban_engine = KanbanEngine(booking_service, event_bus)
        
        # Get columns
        columns = kanban_engine.get_columns()
        column_responses = [column_to_response(col) for col in columns]
        
        # Get all cards organized by column
        cards_by_column = kanban_engine.get_all_cards()
        card_responses = {}
        
        for column_id, cards in cards_by_column.items():
            card_responses[column_id] = [card_to_response(card) for card in cards]
        
        return KanbanBoardResponse(
            columns=column_responses,
            cards=card_responses
        )
        
    except Exception as e:
        logger.error(f"Error getting Kanban board: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Kanban board"
        )

@router.get("/columns", response_model=List[KanbanColumnResponse])
async def get_kanban_columns(
    db: Session = Depends(get_db)
):
    """Get all Kanban columns"""
    try:
        # Initialize services
        booking_repo = BookingRepository(db)
        booking_service = BookingDomainService(db, event_bus)
        kanban_engine = KanbanEngine(booking_service, event_bus)
        
        # Get columns
        columns = kanban_engine.get_columns()
        return [column_to_response(col) for col in columns]
        
    except Exception as e:
        logger.error(f"Error getting Kanban columns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Kanban columns"
        )

@router.get("/columns/{column_id}/cards", response_model=List[KanbanCardResponse])
async def get_column_cards(
    column_id: str,
    db: Session = Depends(get_db)
):
    """Get all cards in a specific column"""
    try:
        # Initialize services
        booking_repo = BookingRepository(db)
        booking_service = BookingDomainService(db, event_bus)
        kanban_engine = KanbanEngine(booking_service, event_bus)
        
        # Get cards for column
        cards = kanban_engine.get_cards_for_column(column_id)
        return [card_to_response(card) for card in cards]
        
    except Exception as e:
        logger.error(f"Error getting cards for column {column_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get cards for column {column_id}"
        )

@router.post("/cards/{card_id}/move", response_model=KanbanCardResponse)
async def move_card(
    card_id: int,
    move_request: MoveCardRequest,
    db: Session = Depends(get_db)
):
    """Move a card to a different column"""
    try:
        # Initialize services
        booking_repo = BookingRepository(db)
        booking_service = BookingDomainService(db, event_bus)
        kanban_engine = KanbanEngine(booking_service, event_bus)
        
        # Move card
        success = await kanban_engine.move_card(
            card_id=card_id,
            to_column_id=move_request.to_column_id,
            employee_id=move_request.employee_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to move card"
            )
        
        # Return updated card
        # In a real implementation, we would fetch the updated card
        # For now, we'll return a simple response
        return KanbanCardResponse(
            id=card_id,
            reference="REF-20230101-0001",  # Placeholder
            title="Studio Session - 2h",  # Placeholder
            client_name="John Doe",  # Placeholder
            start_time="2023-01-01T10:00:00",  # Placeholder
            end_time="2023-01-01T12:00:00",  # Placeholder
            state="confirmed",  # Placeholder
            column_id=move_request.to_column_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving card {card_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to move card"
        )