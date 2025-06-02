from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.services.calendar_event import CalendarEventService
from backend.app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
from backend.app.models.user import User, UserRole
from backend.app.api.routes.auth import get_current_admin, get_current_manager

router = APIRouter(prefix="/calendar-events", tags=["calendar-events"])

@router.get("/", response_model=List[CalendarEventResponse])
async def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_manager)):
    service = CalendarEventService(db)
    return service.get_events(skip=skip, limit=limit)

@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_manager)):
    service = CalendarEventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event

@router.post("/", response_model=CalendarEventResponse)
async def create_event(event_data: CalendarEventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = CalendarEventService(db)
    return service.create_event(event_data)

@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_event(event_id: int, event_data: CalendarEventUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = CalendarEventService(db)
    event = service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event

@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = CalendarEventService(db)
    ok = service.delete_event(event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return {"message": "Событие удалено"}
