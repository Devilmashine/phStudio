import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from backend.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """
    Сервис для работы с Google Calendar через сервисный аккаунт.
    Ключи и параметры берутся из service_account.json.
    """
    def __init__(self):
        self.calendar_id = os.getenv("GOOGLE_CALENDAR_ID") or settings.GOOGLE_CALENDAR_ID
        credentials = service_account.Credentials.from_service_account_file(
            settings.SERVICE_ACCOUNT_FILE,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        self.service = build("calendar", "v3", credentials=credentials)

    def get_available_slots(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Получить список свободных слотов между start_date и end_date.
        Возвращает список словарей с временем начала и конца слота.
        """
        events = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=start_date.isoformat() + 'Z',
            timeMax=end_date.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        # Пример: 1-часовые интервалы с 9 до 21
        slots = []
        busy = []
        for e in events:
            try:
                start_val = e['start']['dateTime'][:-1] if 'dateTime' in e['start'] else None
                end_val = e['end']['dateTime'][:-1] if 'dateTime' in e['end'] else None
                start_dt = datetime.fromisoformat(start_val) if start_val else None
                end_dt = datetime.fromisoformat(end_val) if end_val else None
                logger.info(f"busy slot: start={start_val} ({type(start_dt)}), end={end_val} ({type(end_dt)})")
                if start_dt and end_dt:
                    busy.append((start_dt, end_dt))
            except Exception as ex:
                logger.error(f"Ошибка парсинга busy slot: {e}, ошибка: {ex}")
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        end = end_date.replace(hour=21, minute=0, second=0, microsecond=0)
        while current < end:
            slot_end = current.replace(hour=current.hour+1)
            logger.info(f"Проверка слота: current={current} ({type(current)}), slot_end={slot_end} ({type(slot_end)})")
            for b in busy:
                logger.info(f"Сравнение: b[0]={b[0]} ({type(b[0])}), b[1]={b[1]} ({type(b[1])}), slot_end={slot_end}, current={current}")
            # Проверяем типы перед сравнением
            def safe_compare(b, slot_end, current):
                if not (isinstance(b[0], datetime) and isinstance(b[1], datetime)):
                    logger.error(f"Некорректные типы для сравнения: b[0]={b[0]} ({type(b[0])}), b[1]={b[1]} ({type(b[1])})")
                    return False
                return b[0] < slot_end and b[1] > current
            try:
                if not any(safe_compare(b, slot_end, current) for b in busy):
                    slots.append({"start": current.isoformat(), "end": slot_end.isoformat()})
            except Exception as ex:
                logger.error(f"Ошибка сравнения слотов: {ex}")
            current = slot_end
        return slots

    def create_event(self, summary: str, start_time: datetime, end_time: datetime, description: Optional[str] = None, attendees: Optional[list] = None) -> Dict[str, Any]:
        """
        Создать событие в Google Calendar.
        """
        event = {
            'summary': summary,
            'start': {'dateTime': start_time.isoformat(), 'timeZone': 'Europe/Moscow'},
            'end': {'dateTime': end_time.isoformat(), 'timeZone': 'Europe/Moscow'},
            'description': description or '',
            'attendees': attendees or []
        }
        # Логирование перед созданием события
        logger.info(f"Создание события в Google Calendar: {event}")
        created = self.service.events().insert(calendarId=self.calendar_id, body=event).execute()
        return created

    def update_event(self, event_id: str, **kwargs) -> Dict[str, Any]:
        """
        Обновить событие в Google Calendar по event_id.
        """
        event = self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()
        for key, value in kwargs.items():
            if value is not None:
                event[key] = value
        updated = self.service.events().update(calendarId=self.calendar_id, eventId=event_id, body=event).execute()
        return updated

    def delete_event(self, event_id: str) -> bool:
        """
        Удалить событие из Google Calendar по event_id.
        """
        self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()
        return True

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Получить событие по event_id.
        """
        return self.service.events().get(calendarId=self.calendar_id, eventId=event_id).execute()