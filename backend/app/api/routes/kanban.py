from datetime import date, datetime
import logging
from typing import Dict, Iterable, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models.booking_enhanced import Booking, BookingState, SpaceType

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/kanban", tags=["kanban"])


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
    employee_id: Optional[int] = None


KANBAN_COLUMNS: List[Dict[str, Iterable[BookingState]]] = [
    {
        "id": "new",
        "title": "Новые",
        "order": 1,
        "color": "#3B82F6",
        "states": (BookingState.DRAFT, BookingState.PENDING),
    },
    {
        "id": "confirmed",
        "title": "Подтверждено",
        "order": 2,
        "color": "#10B981",
        "states": (BookingState.CONFIRMED, BookingState.RESCHEDULED),
    },
    {
        "id": "in_progress",
        "title": "В процессе",
        "order": 3,
        "color": "#F59E0B",
        "states": (BookingState.IN_PROGRESS,),
    },
    {
        "id": "completed",
        "title": "Завершено",
        "order": 4,
        "color": "#6B7280",
        "states": (BookingState.COMPLETED,),
    },
    {
        "id": "cancelled",
        "title": "Отменено",
        "order": 5,
        "color": "#EF4444",
        "states": (BookingState.CANCELLED, BookingState.NO_SHOW),
    },
]


def _state_to_column_map() -> Dict[BookingState, str]:
    mapping: Dict[BookingState, str] = {}
    for column in KANBAN_COLUMNS:
        for state in column["states"]:
            mapping[state] = column["id"]
    return mapping


def _column_by_id(column_id: str) -> Optional[Dict[str, Iterable[BookingState]]]:
    return next((column for column in KANBAN_COLUMNS if column["id"] == column_id), None)


def _serialize_column(column: Dict[str, Iterable[BookingState]]) -> KanbanColumnResponse:
    return KanbanColumnResponse(
        id=column["id"],
        title=column["title"],
        order=column["order"],
        color=column["color"],
    )


def _serialize_booking(booking: Booking, column_id: str) -> KanbanCardResponse:
    space_label = booking.space_type.value.replace("_", " ").title() if booking.space_type else "Бронирование"
    duration = f"{float(booking.duration_hours):g}ч" if booking.duration_hours else ""
    title = f"{space_label} {duration}".strip()

    return KanbanCardResponse(
        id=booking.id,
        reference=booking.booking_reference,
        title=title or booking.booking_reference,
        client_name=booking.client_name,
        start_time=booking.start_time.isoformat() if booking.start_time else "",
        end_time=booking.end_time.isoformat() if booking.end_time else "",
        state=booking.state.value,
        column_id=column_id,
    )


def _parse_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid date value: {value}")


@router.get("/board", response_model=KanbanBoardResponse)
def get_kanban_board(
    date_from: Optional[str] = Query(None, description="Filter bookings from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter bookings until date (YYYY-MM-DD)"),
    client_name: Optional[str] = Query(None, description="Filter by client name"),
    state: Optional[str] = Query(None, description="Filter by booking state"),
    space_type: Optional[str] = Query(None, description="Filter by space type"),
    db: Session = Depends(get_db),
):
    """Return Kanban columns and cards backed by real booking data."""

    try:
        query = db.query(Booking).filter(Booking.is_deleted.is_(False))

        start_date = _parse_date(date_from)
        end_date = _parse_date(date_to)

        if start_date:
            query = query.filter(Booking.booking_date >= start_date)
        if end_date:
            query = query.filter(Booking.booking_date <= end_date)

        if client_name:
            query = query.filter(Booking.client_name.ilike(f"%{client_name}%"))

        if space_type:
            try:
                query = query.filter(Booking.space_type == SpaceType(space_type))
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid space type")

        state_filter: Optional[List[BookingState]] = None
        if state:
            try:
                state_filter = [BookingState(state)]
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking state")

        state_map = _state_to_column_map()
        tracked_states = list(state_map.keys())
        if state_filter:
            tracked_states = state_filter

        query = query.filter(Booking.state.in_(tracked_states))

        bookings = query.order_by(Booking.start_time.asc()).all()

        cards: Dict[str, List[KanbanCardResponse]] = {column["id"]: [] for column in KANBAN_COLUMNS}

        for booking in bookings:
            column_id = state_map.get(booking.state)
            if not column_id:
                continue
            if state_filter and booking.state not in state_filter:
                continue
            cards[column_id].append(_serialize_booking(booking, column_id))

        columns = [_serialize_column(column) for column in sorted(KANBAN_COLUMNS, key=lambda c: c["order"])]

        return KanbanBoardResponse(columns=columns, cards=cards)

    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to build kanban board")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get Kanban board",
        ) from exc


@router.get("/columns", response_model=List[KanbanColumnResponse])
def get_kanban_columns() -> List[KanbanColumnResponse]:
    """Return static kanban column configuration."""
    return [_serialize_column(column) for column in sorted(KANBAN_COLUMNS, key=lambda c: c["order"])]


@router.get("/columns/{column_id}/cards", response_model=List[KanbanCardResponse])
def get_column_cards(
    column_id: str,
    db: Session = Depends(get_db),
):
    """Return cards for a specific column backed by live booking data."""

    column = _column_by_id(column_id)
    if not column:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Column not found")

    states = list(column["states"])

    query = (
        db.query(Booking)
        .filter(Booking.is_deleted.is_(False), Booking.state.in_(states))
        .order_by(Booking.start_time.asc())
    )

    bookings = query.all()
    return [_serialize_booking(booking, column_id) for booking in bookings]


@router.post("/cards/{card_id}/move", response_model=KanbanCardResponse)
def move_card(
    card_id: int,
    move_request: MoveCardRequest,
    db: Session = Depends(get_db),
):
    """Transition a booking to a new state that matches the target column."""

    column = _column_by_id(move_request.to_column_id)
    if not column:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target column not found")

    target_state = next(iter(column["states"]), None)
    if not target_state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Column has no target state")

    booking: Optional[Booking] = (
        db.query(Booking)
        .filter(Booking.id == card_id, Booking.is_deleted.is_(False))
        .first()
    )

    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

    if booking.state == target_state:
        return _serialize_booking(booking, move_request.to_column_id)

    if not booking.can_transition_to(target_state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition booking from {booking.state.value} to {target_state.value}",
        )

    employee_id = move_request.employee_id or 0
    transitioned = booking.transition_to(target_state, employee_id)
    if not transitioned:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State transition failed")

    try:
        db.add(booking)
        db.commit()
        db.refresh(booking)
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to persist booking state transition")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to move card") from exc

    return _serialize_booking(booking, move_request.to_column_id)