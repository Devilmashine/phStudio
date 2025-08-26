from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.booking import BookingService
from app.schemas.booking import Booking, BookingCreate, BookingStatusUpdate, MessageResponse
from app.models.user import User, UserRole
from app.deps import get_current_admin, get_current_manager

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
    from app.services.telegram.booking_notifications import booking_notification_service
    from app.models.telegram import BookingData, Language
    
    service = BookingService(db)
    try:
        db_booking = service.create_booking(booking_data)
        
        # Send notification using new system
        try:
            notification_booking_data = BookingData(
                id=str(db_booking.id),
                service="Студийная фотосессия",
                date=booking_data.date,
                time_slots=[f"{booking_data.start_time.strftime('%H:%M')}-{booking_data.end_time.strftime('%H:%M')}"],
                client_name=booking_data.client_name,
                client_phone=booking_data.client_phone,
                people_count=getattr(booking_data, 'people_count', 1),
                total_price=float(booking_data.total_price),
                description=booking_data.notes,
                status="pending"
            )
            
            await booking_notification_service.send_booking_notification(
                booking_data=notification_booking_data,
                language=Language.RU,
                queue=True
            )
        except Exception as e:
            # Log notification error but don't fail the booking
            import logging
            logging.getLogger(__name__).error(f"Failed to send notification for booking {db_booking.id}: {e}")
        
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
    from app.services.telegram.booking_notifications import booking_notification_service
    from app.models.telegram import BookingData, Language
    
    service = BookingService(db)
    db_booking = service.create_booking(booking_data)
    
    # Send notification using new system
    try:
        notification_booking_data = BookingData(
            id=str(db_booking.id),
            service="Студийная фотосессия",
            date=booking_data.date,
            time_slots=[f"{booking_data.start_time.strftime('%H:%M')}-{booking_data.end_time.strftime('%H:%M')}"],
            client_name=booking_data.client_name,
            client_phone=booking_data.client_phone,
            people_count=getattr(booking_data, 'people_count', 1),
            total_price=float(booking_data.total_price),
            description=booking_data.notes,
            status="pending"
        )
        
        await booking_notification_service.send_booking_notification(
            booking_data=notification_booking_data,
            language=Language.RU,
            queue=True
        )
    except Exception as e:
        # Log notification error but don't fail the booking
        import logging
        logging.getLogger(__name__).error(f"Failed to send notification for booking {db_booking.id}: {e}")
    
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
