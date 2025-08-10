from .base import Base
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime


class GalleryImage(Base):
    __tablename__ = "gallery_images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    url = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)
