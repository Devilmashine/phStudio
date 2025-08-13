from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.booking import BookingService
from app.schemas.booking import Booking, BookingCreate
from app.models.user import User, UserRole
from app.api.routes.auth import get_current_admin, get_current_manager
from app.services.telegram import telegram_service

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


@router.post("/", response_model=Booking)
async def create_booking(
    booking_data: BookingCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)
):
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
