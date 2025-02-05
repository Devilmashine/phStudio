# Убедитесь, что у вас установлены необходимые зависимости:
# pip install fastapi
# pip install python-dotenv
# pip install uvicorn
# pip install google-api-python-client
# pip install python-telegram-bot

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import asyncio
import os
from dotenv import load_dotenv
import logging
import os
from logging.handlers import RotatingFileHandler

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
from app.services.google_calendar import GoogleCalendarService
from app.services.telegram_bot import TelegramBotService

app = FastAPI()

# Настройка CORS с поддержкой credentials
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Точный домен фронтенда
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
    calendar_service = GoogleCalendarService.get_instance()
    logger.info("Google Calendar Service успешно инициализирован")
except Exception as e:
    logger.error(f"Ошибка инициализации Google Calendar Service: {str(e)}")
    calendar_service = None

try:
    telegram_service = TelegramBotService.get_instance(os.getenv('TELEGRAM_BOT_TOKEN'))
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
        booking_message = (
            f"🎨 Новое бронирование:\n"
            f"Услуга: {booking_data.service}\n"
            f"Дата: {booking_data.date}\n"
            f"Время: {', '.join(booking_data.times)}\n"
            f"Клиент: {booking_data.name}\n"
            f"Телефон: {booking_data.phone}\n"
            f"Сумма: {booking_data.totalPrice} руб."
        )
        
        # Отправка уведомления в Telegram
        telegram_notification_sent = await telegram_service.send_booking_notification(booking_message)
        
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

@app.post("/api/calendar/events")
async def create_calendar_event(event_data: CalendarEventData):
    try:
        if calendar_service is None:
            logger.error("Google Calendar Service не инициализирован")
            raise HTTPException(status_code=500, detail="Сервис календаря недоступен")
        
        # Парсинг времени начала
        start_datetime = datetime.fromisoformat(event_data.start_time)
        
        # Создание события с учетом длительности
        event = {
            'summary': event_data.title,
            'description': event_data.description,
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': (start_datetime + timedelta(hours=event_data.duration_hours)).isoformat(),
                'timeZone': 'Europe/Moscow',
            },
        }
        
        calendar_event = calendar_service.create_event(event)
        
        if not calendar_event:
            logger.error("Не удалось создать событие в календаре")
            raise HTTPException(status_code=500, detail="Не удалось создать событие в календаре")
        
        return {
            "id": calendar_event.get('id'),
            "link": calendar_event.get('htmlLink'),
            "status": "success"
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
        booking_message = (
            f"🎨 Новое бронирование:\n"
            f"Дата: {notification_data.date}\n"
            f"Время: {', '.join(notification_data.times)}\n"
            f"Клиент: {notification_data.name}\n"
            f"Телефон: {notification_data.phone}\n"
            f"Сумма: {notification_data.totalPrice} руб."
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
