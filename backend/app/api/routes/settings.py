from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...schemas.settings import StudioSettings, StudioSettingsCreate, StudioSettingsUpdate
from ...services.settings import StudioSettingsService
from ...core.database import get_db
from .auth import get_current_admin
from ...models.user import User

router = APIRouter()

@router.get("/", response_model=StudioSettings)
def get_studio_settings(db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = StudioSettingsService(db)
    settings = service.get_settings()
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки студии не найдены")
    return settings

@router.post("/", response_model=StudioSettings)
def create_studio_settings(settings_data: StudioSettingsCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = StudioSettingsService(db)
    settings = service.create_settings(settings_data)
    return settings

@router.put("/", response_model=StudioSettings)
def update_studio_settings(settings_data: StudioSettingsUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_admin)):
    service = StudioSettingsService(db)
    settings = service.update_settings(settings_data)
    if not settings:
        raise HTTPException(status_code=404, detail="Настройки студии не найдены")
    return settings
