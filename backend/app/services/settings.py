import json
from sqlalchemy.orm import Session
from backend.app.models.settings import StudioSettings
from backend.app.schemas.settings import StudioSettingsCreate, StudioSettingsUpdate
from typing import Optional

class StudioSettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self) -> Optional[StudioSettings]:
        return self.db.query(StudioSettings).first()

    import json
    def create_settings(self, settings_data: StudioSettingsCreate) -> StudioSettings:
        data = settings_data.dict()
        data['work_days'] = json.dumps(data['work_days'])
        if data.get('holidays') is not None:
            data['holidays'] = json.dumps(data['holidays'])
        settings = StudioSettings(**data)
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update_settings(self, settings_data: StudioSettingsUpdate) -> Optional[StudioSettings]:
        import json
        settings = self.get_settings()
        if not settings:
            return None
        for field, value in settings_data.dict(exclude_unset=True).items():
            if field in ('work_days', 'holidays') and value is not None:
                value = json.dumps(value)
            setattr(settings, field, value)
        self.db.commit()
        self.db.refresh(settings)
        return settings
