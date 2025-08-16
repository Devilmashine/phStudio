from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.core.database import get_db
from app.services.calendar_event import CalendarEventService
from app.schemas.calendar_event import CalendarEventCreate, CalendarEventUpdate, CalendarEventResponse
from app.models.user import User, UserRole
from app.api.routes.auth import get_current_admin, get_current_manager
from fastapi.responses import Response, StreamingResponse
from ics import Calendar, Event as IcsEvent
from secrets import token_urlsafe
from app.models.calendar_event import CalendarEvent

router = APIRouter(
    tags=["calendar-events"],
    # Отключаем автоматический редирект при отсутствии завершающего слеша
    redirect_slashes=False,
)


@router.get("/", response_model=List[CalendarEventResponse])
async def get_events(
    skip: int = 0,
    limit: int = 100,
    start_date: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(None, description="End date in YYYY-MM-DD format"),
    event_status: str = None,
    db: Session = Depends(get_db),
):
    try:
        # Convert string dates to datetime objects
        start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

        service = CalendarEventService(db)
        events = service.get_events(
            skip=skip,
            limit=limit,
            start_date=start_dt,
            end_date=end_dt,
            status=event_status,
        )
        return events
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Неверный формат даты: {str(e)}")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager),
):
    service = CalendarEventService(db)
    event = service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.post("/", response_model=CalendarEventResponse)
async def create_event(
    event_data: CalendarEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = CalendarEventService(db)
    return service.create_event(event_data)


@router.put("/{event_id}", response_model=CalendarEventResponse)
async def update_event(
    event_id: int,
    event_data: CalendarEventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = CalendarEventService(db)
    event = service.update_event(event_id, event_data)
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.delete("/{event_id}")
async def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = CalendarEventService(db)
    ok = service.delete_event(event_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return {"message": "Событие удалено"}


@router.get("/ical/{user_id}/{token}")
async def get_ical_for_user(user_id: int, token: str, db: Session = Depends(get_db)):
    # Проверка токена пользователя (реализовать хранение токена в User)
    user = db.query(User).filter(User.id == user_id).first()
    if not user or getattr(user, "ical_token", None) != token:
        raise HTTPException(status_code=403, detail="Недействительный токен")
    events = db.query(CalendarEvent).all()
    cal = Calendar()
    for e in events:
        ics_event = IcsEvent()
        ics_event.name = e.title
        ics_event.begin = e.start_time
        ics_event.end = e.end_time
        ics_event.description = e.description or ""
        cal.events.add(ics_event)
    return Response(content=str(cal), media_type="text/calendar")


@router.get("/{event_id}/ical")
async def get_ical_for_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(CalendarEvent).filter(CalendarEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    cal = Calendar()
    ics_event = IcsEvent()
    ics_event.name = event.title
    ics_event.begin = event.start_time
    ics_event.end = event.end_time
    ics_event.description = event.description or ""
    cal.events.add(ics_event)
    return Response(content=str(cal), media_type="text/calendar")


@router.post("/ical-token/reset/{user_id}", response_model=dict)
async def reset_ical_token(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    user.ical_token = token_urlsafe(32)
    db.commit()
    db.refresh(user)
    return {"ical_token": user.ical_token}
