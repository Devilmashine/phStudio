from sqlalchemy import Column, Integer, String, DateTime, Index
from datetime import datetime, timezone
from .base import Base


class Client(Base):
    __tablename__ = "clients"
    __table_args__ = (
        Index("idx_clients_phone", "phone"),
        Index("idx_clients_email", "email"),
        Index("idx_clients_name", "name"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=False, unique=True)
    email = Column(String(255), nullable=True)
    
    # Additional client information for photo studio
    notes = Column(String(1000), nullable=True)
    preferred_contact_method = Column(String(20), default="phone", nullable=False)  # phone, email, telegram
    
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
