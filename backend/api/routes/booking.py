from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from backend.app.models.booking import Booking as BookingModel
from backend.app.schemas.booking import Booking, BookingCreate
from backend.app.core.database import get_db
from backend.app.services.telegram import telegram_service

router = APIRouter()

@router.get("/", response_model=List[Booking])
async def get_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение списка бронирований"""
    bookings = db.query(BookingModel).offset(skip).limit(limit).all()
    return bookings

@router.post("/", response_model=Booking)
async def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db)
):
    """Создание нового бронирования"""
    db_booking = BookingModel(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    """Получение бронирования по ID"""
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking 