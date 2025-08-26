from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.booking import BookingService
from app.schemas.booking import Booking, BookingCreate, BookingStatusUpdate, MessageResponse
from app.models.user import User, UserRole
from app.api.routes.auth import get_current_admin, get_current_manager
from app.services.telegram_bot import TelegramBotService

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/", response_model=List[Booking])
async def get_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager),
):
    service = BookingService(db)
    return service.get_bookings(skip=skip, limit=limit)


@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager),
):
    service = BookingService(db)
    booking = service.get_booking(booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return booking
@router.patch("/{booking_id}/status", response_model=Booking)
async def update_booking_status(
    booking_id: int,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_manager)
):
    """
    Эндпоинт для обновления статуса бронирования.
    Доступен для менеджеров и администраторов.
    """
    service = BookingService(db)
    booking = service.update_booking_status(booking_id, status_update.status)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return booking

@router.post("/public/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_public_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    """
    Публичный эндпоинт для создания бронирования клиентом.
    Не требует аутентификации.
    """
    from app.core.errors import BookingError
    
    service = BookingService(db)
    try:
        db_booking = service.create_booking(booking_data)
        telegram_service = TelegramBotService()
        await telegram_service.send_booking_notification(
            message="Новое бронирование",
            service="Студийная фотосессия",
            date=booking_data.date.strftime('%Y-%m-%d'),
            times=[booking_data.start_time.strftime('%H:%M'), booking_data.end_time.strftime('%H:%M')],
            name=booking_data.client_name,
            phone=booking_data.client_phone,
            total_price=int(booking_data.total_price),
            people_count=1
        )
        return db_booking
    except BookingError as e:
        # Return specific validation error messages
        if e.code == "TIME_CONFLICT":
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=e.message)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Произошла внутренняя ошибка при создании бронирования.")

@router.post("/", response_model=Booking)
async def create_booking(
    booking_data: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
    service = BookingService(db)
    db_booking = service.create_booking(booking_data)
    telegram_service = TelegramBotService()
    await telegram_service.send_booking_notification(
        message="Новое бронирование (админ)",
        service="Студийная фотосессия",
        date=booking_data.date.strftime('%Y-%m-%d'),
        times=[booking_data.start_time.strftime('%H:%M'), booking_data.end_time.strftime('%H:%M')],
        name=booking_data.client_name,
        phone=booking_data.client_phone,
        total_price=int(booking_data.total_price),
        people_count=1
    )
    return db_booking


@router.put("/{booking_id}", response_model=Booking)
async def update_booking(
    booking_id: int,
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = BookingService(db)
    booking = service.update_booking(booking_id, booking_data)
    if not booking:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return booking


@router.delete("/{booking_id}", response_model=MessageResponse)
async def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    service = BookingService(db)
    ok = service.delete_booking(booking_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Бронирование не найдено")
    return {"message": "Бронирование удалено"}
