from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import time

class StudioSettingsBase(BaseModel):
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

class StudioSettings(StudioSettingsBase):
    id: int

    class Config:
        from_attributes = True
