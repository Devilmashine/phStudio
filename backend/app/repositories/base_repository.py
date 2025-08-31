from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Type
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

T = TypeVar('T')  # Model type

class BaseRepository(ABC, Generic[T]):
    """Base repository with common database operations"""
    
    def __init__(self, db: Session, model: Type[T]):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get entity by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all entities with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, entity: T) -> T:
        """Create a new entity"""
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def update(self, entity: T) -> T:
        """Update an existing entity"""
        self.db.commit()
        self.db.refresh(entity)
        return entity
    
    def delete(self, entity: T) -> bool:
        """Delete an entity"""
        self.db.delete(entity)
        self.db.commit()
        return True
    
    def delete_by_id(self, id: int) -> bool:
        """Delete an entity by ID"""
        entity = self.get_by_id(id)
        if entity:
            return self.delete(entity)
        return False
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        try:
            yield self
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise