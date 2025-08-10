import json
from sqlalchemy.orm import Session
from ..models.settings import StudioSettings
from ..schemas.settings import StudioSettingsCreate, StudioSettingsUpdate
from typing import Optional


class StudioSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self) -> Optional[StudioSettings]:
        return self.db.query(StudioSettings).first()

    def create_settings(self, settings_data: StudioSettingsCreate) -> StudioSettings:
        data = settings_data.model_dump()
        # Поля JSON должны быть строками
        data["work_days"] = json.dumps(data["work_days"])
        if data.get("holidays") is not None:
            data["holidays"] = json.dumps(data["holidays"])

        settings = StudioSettings(**data)
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update_settings(
        self, settings_data: StudioSettingsUpdate
    ) -> Optional[StudioSettings]:
        settings = self.get_settings()
        if not settings:
            return None

        update_data = settings_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field in ("work_days", "holidays") and value is not None:
                value = json.dumps(value)
            setattr(settings, field, value)

        self.db.commit()
        self.db.refresh(settings)
        return settings
