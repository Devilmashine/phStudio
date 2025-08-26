from .base import Base
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Index
from datetime import datetime, timezone


class News(Base):
    __tablename__ = "news"
    __table_args__ = (
        Index("idx_news_published", "published"),
        Index("idx_news_author", "author_id"),
        Index("idx_news_created_at", "created_at"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    
    # Use timezone-aware datetime for PostgreSQL
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Use Boolean instead of Integer for published status
    published = Column(Boolean, default=True, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Additional fields for better news management
    summary = Column(String(500), nullable=True)  # Short summary
    tags = Column(String(255), nullable=True)  # Comma-separated tags
    featured = Column(Boolean, default=False, nullable=False)  # Featured news
