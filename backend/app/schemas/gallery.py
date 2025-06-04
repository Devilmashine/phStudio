from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GalleryImageBase(BaseModel):
    description: Optional[str] = None

class GalleryImageCreate(GalleryImageBase):
    pass

class GalleryImage(GalleryImageBase):
    id: int
    filename: str
    url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True
