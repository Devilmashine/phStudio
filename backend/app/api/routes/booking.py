from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.core.database import get_db
from backend.app.models.booking import Booking as BookingModel
from backend.app.schemas.booking import Booking, BookingCreate
from app.services.telegram import telegram_service

router = APIRouter()

@router.get("/", response_model=List[Booking])
async def get_bookings(db: Session = Depends(get_db)):
    return db.query(BookingModel).all()

@router.post("/", response_model=Booking)
async def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    db_booking = BookingModel(**booking.model_dump())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # Отправляем уведомление в Telegram
    await telegram_service.send_booking_notification(booking.model_dump())
    
    return db_booking

@router.get("/{booking_id}", response_model=Booking)
async def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    return booking

@router.delete("/{booking_id}")
async def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Бронь не найдена")
    
    # Отправляем уведомление об отмене в Telegram
    await telegram_service.send_cancellation_notification({
        "date": booking.date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "client_name": booking.client_name,
        "client_phone": booking.client_phone
    })
    
    db.delete(booking)
    db.commit()
    return {"message": "Бронь успешно отменена"} 