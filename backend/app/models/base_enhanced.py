from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr

class EnhancedBase:
    __abstract__ = True
    
    @declared_attr
    def created_at(cls):
        return Column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    @declared_attr
    def updated_at(cls):
        return Column(DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False)
    
    @declared_attr
    def created_by(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def updated_by(cls):
        return Column(Integer, nullable=True)
    
    @declared_attr
    def version(cls):
        return Column(Integer, default=1, nullable=False)  # Optimistic locking