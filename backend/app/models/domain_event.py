from sqlalchemy import Column, Integer, String, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .base_enhanced import EnhancedBase
from .base import Base

class DomainEvent(Base, EnhancedBase):
    __tablename__ = "domain_events"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True)
    event_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    aggregate_id = Column(String(50), nullable=False)
    aggregate_type = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_data = Column(JSON, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    occurred_at = Column(DateTime(timezone=True), default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        Index("idx_event_aggregate", "aggregate_type", "aggregate_id"),
        Index("idx_event_type", "event_type"),
        Index("idx_event_occurred", "occurred_at"),
        # Inherited from EnhancedBase: created_at, updated_at indexes
    )