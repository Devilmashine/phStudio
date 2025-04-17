# Убедитесь, что у вас установлены необходимые зависимости:
# pip install fastapi
# pip install python-dotenv
# pip install uvicorn
# pip install google-api-python-client
# pip install python-telegram-bot

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
import logging
import os
from logging.handlers import RotatingFileHandler
from backend.api.routes.calendar import router as calendar_router
from backend.api.routes.telegram import router as telegram_router
from typing import List, Dict, Any
from backend.app.services.telegram_templates import booking_message_template
import sentry_sdk

# Настройка логирования
def setup_logging():
    log_dir = os.path.join(os.path.dirname(__file__), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'app.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),  # Вывод в консоль
            RotatingFileHandler(
                log_file, 
                maxBytes=10*1024*1024,  # 10 МБ
                backupCount=5
            )
        ]
    )

# Вызываем настройку логирования перед инициализацией приложения
setup_logging()

logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Импорт сервисов
from backend.app.services.google_calendar import GoogleCalendarService
from backend.app.services.telegram_bot import TelegramBotService

app = FastAPI()
app.include_router(calendar_router)
app.include_router(telegram_router)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_time_slots(start_hour=9, end_hour=20, slot_duration=1):
    slots = []
    current_time = datetime.strptime(f"{start_hour:02d}:00", "%H:%M")
    end_time = datetime.strptime(f"{end_hour:02d}:00", "%H:%M")
    
    while current_time < end_time:
        next_time = current_time + timedelta(hours=slot_duration)
        slots.append({
            "startTime": current_time.strftime("%H:%M"),
            "endTime": next_time.strftime("%H:%M"),
            "available": True,
            "bookedPercentage": 0
        })
        current_time = next_time
    
    return slots

# Инициализация сервисов с обработкой ошибок
try:
    calendar_service = GoogleCalendarService()
    logger.info("Google Calendar Service успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации Google Calendar Service: {str(e)}")
    calendar_service = None

try:
    telegram_service = TelegramBotService()
    logger.info("Telegram Bot Service успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации Telegram Bot Service: {str(e)}")
    telegram_service = None

class BookingData(BaseModel):
    date: str
    times: list[str]
    name: str
    phone: str
    totalPrice: int
    service: str = "Студийная фотосессия"

class CalendarEventData(BaseModel):
    title: str
    description: str
    start_time: str
    duration_hours: int = Field(default=1, ge=1, le=8)

class TelegramNotificationData(BaseModel):
    name: str
    phone: str
    date: str
    times: list[str]
    totalPrice: int

@app.get("/api/calendar/available-slots")
async def get_available_slots(date: str):
    # Временная заглушка для тестирования
    return {
        "date": date,
        "isAvailable": True,
        "status": "available",
        "slots": generate_time_slots()
    }

@app.post("/api/bookings")
async def create_booking(booking_data: BookingData):
    try:
        # Проверка инициализации сервисов
        if calendar_service is None:
            logger.error("Google Calendar Service не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис календаря недоступен")
        
        if telegram_service is None:
            logger.error("Telegram Bot Service не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис уведомлений недоступен")

        # Создание события в Google Calendar
        event_data = {
            'summary': f'Фотосессия для {booking_data.name}',
            'description': f'Бронирование фотостудии. Клиент: {booking_data.name}, Телефон: {booking_data.phone}',
            'start': {
                'dateTime': f'{booking_data.date}T{booking_data.times[0]}:00',
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': f'{booking_data.date}T{booking_data.times[-1].split("-")[1]}:00',
                'timeZone': 'Europe/Moscow',
            },
        }
        
        calendar_event = calendar_service.create_event(event_data)
        
        if not calendar_event:
            logger.error("Не удалось создать событие в календаре")
            raise HTTPException(status_code=500, detail="Не удалось создать событие в календаре")
        
        # Формирование сообщения для Telegram
        booking_message = booking_message_template(
            service=booking_data.service,
            date=booking_data.date,
            times=booking_data.times,
            name=booking_data.name,
            phone=booking_data.phone,
            total_price=booking_data.totalPrice
        )
        logger.info(f"Пробую отправить уведомление в Telegram: {booking_message}")
        telegram_notification_sent = await telegram_service.send_booking_notification(
            message=booking_message,
            booking_id=calendar_event.get('id'),
            service=booking_data.service,
            date=booking_data.date,
            times=booking_data.times,
            name=booking_data.name,
            phone=booking_data.phone,
            total_price=booking_data.totalPrice
        )
        logger.info(f"Результат отправки в Telegram: {telegram_notification_sent}")
        if not telegram_notification_sent:
            logger.warning("Не удалось отправить уведомление в Telegram")
        
        return {
            "message": "Бронирование создано",
            "booking_id": calendar_event.get('id', 'unknown'),
            "calendar_link": calendar_event.get('htmlLink', ''),
            "telegram_notification": telegram_notification_sent,
            "details": {
                "date": booking_data.date,
                "times": booking_data.times,
                "name": booking_data.name,
                "phone": booking_data.phone,
                "total_price": booking_data.totalPrice
            }
        }
    except Exception as e:
        logger.error(f"Ошибка создания бронирования: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/calendar/events", response_model=Dict[str, Any])
async def create_calendar_event(event_data: CalendarEventData):
    try:
        if calendar_service is None:
            logger.error("Google Calendar Service не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис календаря недоступен")
        
        # Парсинг времени начала
        start_datetime = datetime.fromisoformat(event_data.start_time)
        end_datetime = start_datetime + timedelta(hours=event_data.duration_hours)
        
        # Передаём параметры по сигнатуре create_event
        calendar_event = calendar_service.create_event(
            summary=event_data.title,
            start_time=start_datetime,
            end_time=end_datetime,
            description=event_data.description
        )
        
        if not calendar_event:
            logger.error("Не удалось создать событие в календаре")
            raise HTTPException(status_code=500, detail="Не удалось создать событие в календаре")
        
        # Формирование сообщения для Telegram
        booking_message = booking_message_template(
            service=event_data.title,
            date=start_datetime.strftime('%d.%m.%Y'),
            times=[start_datetime.strftime('%H:%M'), end_datetime.strftime('%H:%M')],
            name=event_data.title,
            phone="",
            total_price=0
        )
        logger.info(f"Пробую отправить уведомление в Telegram (calendar.events): {booking_message}")
        telegram_notification_sent = await telegram_service.send_booking_notification(booking_message)
        logger.info(f"Результат отправки в Telegram (calendar.events): {telegram_notification_sent}")
        if not telegram_notification_sent:
            logger.warning("Не удалось отправить уведомление в Telegram (calendar.events)")
        
        return {
            "id": calendar_event.get('id'),
            "link": calendar_event.get('htmlLink'),
            "status": "success",
            "telegram_notification": telegram_notification_sent
        }
    except Exception as e:
        logger.error(f"Ошибка создания события в календаре: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/telegram/notify")
async def send_telegram_notification(notification_data: TelegramNotificationData):
    try:
        if telegram_service is None:
            logger.error("Telegram Bot Service не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис уведомлений недоступен")
        
        # Формирование сообщения
        booking_message = booking_message_template(
            service=notification_data.service,
            date=notification_data.date,
            times=notification_data.times,
            name=notification_data.name,
            phone=notification_data.phone,
            total_price=notification_data.totalPrice
        )
        
        # Отправка уведомления
        telegram_notification_sent = await telegram_service.send_booking_notification(booking_message)
        
        if not telegram_notification_sent:
            logger.warning("Не удалось отправить уведомление в Telegram")
            raise HTTPException(status_code=500, detail="Не удалось отправить уведомление")
        
        return {
            "status": "success",
            "message": "Уведомление отправлено"
        }
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/calendar/events", response_model=List[Dict[str, Any]])
async def get_calendar_events(
    start_date: str = Query(..., description="Дата начала периода, формат YYYY-MM-DD"),
    end_date: str = Query(..., description="Дата конца периода, формат YYYY-MM-DD")
):
    try:
        if calendar_service is None:
            logger.error("Google Calendar Service не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис календаря недоступен")
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date) + timedelta(days=1)
        events = calendar_service.service.events().list(
            calendarId=calendar_service.calendar_id,
            timeMin=start_dt.isoformat() + 'Z',
            timeMax=end_dt.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        return events
    except Exception as e:
        logger.error(f"Ошибка получения событий календаря: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/telegram/webhook")
async def telegram_webhook(request: Request):
    data = await request.json()
    if "callback_query" in data:
        callback = data["callback_query"]
        callback_data = callback.get("data", "")
        chat_id = callback["message"]["chat"]["id"]
        message_id = callback["message"]["message_id"]
        user = callback["from"]
        booking_id = None
        action = None
        if ":" in callback_data:
            action, booking_id = callback_data.split(":", 1)
        # TODO: Проверка прав администратора по user["id"]
        if action == "confirm":
            # Здесь логика подтверждения брони (например, обновить статус в БД)
            # Отправить уведомление клиенту, отредактировать сообщение
            # Пример:
            await telegram_service.send_booking_notification(
                message=f"✅ Бронирование подтверждено админом {user['first_name']}",
                booking_id=booking_id
            )
            # Можно также использовать Telegram API для editMessageText
        elif action == "reject":
            await telegram_service.send_booking_notification(
                message=f"❌ Бронирование отклонено админом {user['first_name']}",
                booking_id=booking_id
            )
        # Ответить callback_query (Telegram API)
        return {"ok": True}
    return {"ok": False}

sentry_sdk.init(
    dsn="ВАШ_SENTRY_DSN", # TODO: заменить на реальный DSN
    traces_sample_rate=1.0,
    environment="production"
)
