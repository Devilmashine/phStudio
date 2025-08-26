from .base import Base
from sqlalchemy import Column, Integer, String, DateTime, Text, Index, Boolean
from datetime import datetime, timezone


class GalleryImage(Base):
    __tablename__ = "gallery_images"
    __table_args__ = (
        Index("idx_gallery_filename", "filename"),
        Index("idx_gallery_uploaded_at", "uploaded_at"),
        Index("idx_gallery_category", "category"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, unique=True)
    url = Column(String(500), nullable=False)  # URL can be longer
    
    # Use timezone-aware datetime for PostgreSQL
    uploaded_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    description = Column(Text, nullable=True)  # Use Text for longer descriptions
    
    # Additional fields for better gallery management
    category = Column(String(100), nullable=True)  # e.g., "portrait", "wedding", "family"
    alt_text = Column(String(255), nullable=True)  # SEO and accessibility
    is_featured = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    file_size = Column(Integer, nullable=True)  # File size in bytes
    image_width = Column(Integer, nullable=True)
    image_height = Column(Integer, nullable=True)
