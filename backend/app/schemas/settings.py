from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import time

class StudioSettingsBase(BaseModel):
    name: str = Field(..., description="Название студии")
    contacts: str = Field(..., description="Контактная информация")
    prices: str = Field(..., description="Цены")
    work_days: List[str] = Field(..., description="Список рабочих дней недели (например, ['mon', 'tue', ...])")
    work_start_time: str = Field(..., description="Время начала работы, формат HH:MM")
    work_end_time: str = Field(..., description="Время окончания работы, формат HH:MM")
    base_price_per_hour: float = Field(..., description="Базовая цена за час")
    weekend_price_multiplier: float = Field(1.5, description="Множитель цены для выходных")
    telegram_notifications_enabled: bool = Field(True)
    email_notifications_enabled: bool = Field(True)
    holidays: Optional[List[str]] = Field(default=None, description="Список праздничных дней (YYYY-MM-DD)")
    min_booking_duration: int = Field(1, description="Минимальная длительность бронирования (часы)")
    max_booking_duration: int = Field(8, description="Максимальная длительность бронирования (часы)")
    advance_booking_days: int = Field(30, description="За сколько дней вперёд можно бронировать")

class StudioSettingsCreate(StudioSettingsBase):
    pass

class StudioSettingsUpdate(StudioSettingsBase):
    pass

from pydantic import model_validator

class StudioSettings(StudioSettingsBase):
    id: int

    @model_validator(mode='before')
    def deserialize_json_fields(cls, data):
        import json
        if hasattr(data, '_asdict'): # Проверка, если это объект ORM
            obj_data = data._asdict()
        elif isinstance(data, dict):
            obj_data = data
        else:
            return data

        work_days = obj_data.get('work_days')
        if isinstance(work_days, str):
            try:
                obj_data['work_days'] = json.loads(work_days)
            except json.JSONDecodeError:
                obj_data['work_days'] = []

        holidays = obj_data.get('holidays')
        if isinstance(holidays, str):
            try:
                obj_data['holidays'] = json.loads(holidays)
            except json.JSONDecodeError:
                obj_data['holidays'] = []

        return obj_data

    class ConfigDict:
        from_attributes = True
