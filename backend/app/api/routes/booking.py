from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ...core.database import get_db
from ...services.booking import BookingService
from ...schemas.booking import Booking, BookingCreate
from ...models.user import User
from .auth import get_current_admin, get_current_manager
from ...services.telegram import telegram_service

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


@router.post("/public/", response_model=Booking, status_code=status.HTTP_201_CREATED)
async def create_public_booking(
    booking_data: BookingCreate, db: Session = Depends(get_db)
):
    """
    Публичный эндпоинт для создания бронирования клиентом.
    Не требует аутентификации.
    """
    service = BookingService(db)
    try:
        db_booking = service.create_booking(booking_data)
        # Отправляем уведомление в Telegram
        await telegram_service.send_booking_notification(booking_data.model_dump())
        return db_booking
    except HTTPException:
        raise
    except Exception:
        # Логируем непредвиденную ошибку
        # logger.error(f"Unexpected error creating public booking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Произошла внутренняя ошибка при создании бронирования.",
        )


@router.post("/", response_model=Booking, dependencies=[Depends(get_current_admin)])
async def create_booking_admin(
    booking_data: BookingCreate, db: Session = Depends(get_db)
):
    """
    Эндпоинт для создания бронирования администратором.
    """
    service = BookingService(db)
    db_booking = service.create_booking(booking_data)

    # Отправляем уведомление в Telegram
    await telegram_service.send_booking_notification(booking_data.model_dump())

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


@router.delete("/{booking_id}")
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
