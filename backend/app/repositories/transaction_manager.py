from typing import ContextManager, Any
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

class TransactionManager:
    """Transaction manager for database operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions"""
        try:
            logger.debug("Starting database transaction")
            yield self
            self.db.commit()
            logger.debug("Database transaction committed")
        except SQLAlchemyError as e:
            logger.error(f"Database error in transaction: {e}")
            self.db.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in transaction: {e}")
            self.db.rollback()
            raise
    
    def flush(self):
        """Flush pending changes to the database"""
        try:
            self.db.flush()
        except SQLAlchemyError as e:
            logger.error(f"Error flushing changes: {e}")
            raise
    
    def refresh(self, instance):
        """Refresh an instance from the database"""
        try:
            self.db.refresh(instance)
        except SQLAlchemyError as e:
            logger.error(f"Error refreshing instance: {e}")
            raise
    
    def add(self, instance):
        """Add an instance to the session"""
        try:
            self.db.add(instance)
        except SQLAlchemyError as e:
            logger.error(f"Error adding instance: {e}")
            raise
    
    def delete(self, instance):
        """Delete an instance from the session"""
        try:
            self.db.delete(instance)
        except SQLAlchemyError as e:
            logger.error(f"Error deleting instance: {e}")
            raise

class UnitOfWork:
    """Unit of Work pattern implementation"""
    
    def __init__(self, db: Session):
        self.db = db
        self.transactions = TransactionManager(db)
        self._repositories = {}
    
    @contextmanager
    def atomic(self):
        """Atomic operation context manager"""
        with self.transactions.transaction() as tx:
            try:
                yield tx
            except Exception:
                # Exception will be re-raised by transaction manager
                raise
    
    def register_repository(self, name: str, repository):
        """Register a repository with the unit of work"""
        self._repositories[name] = repository
    
    def get_repository(self, name: str):
        """Get a registered repository"""
        return self._repositories.get(name)
    
    def commit(self):
        """Commit all changes"""
        try:
            self.db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise
    
    def rollback(self):
        """Rollback all changes"""
        try:
            self.db.rollback()
        except SQLAlchemyError as e:
            logger.error(f"Error rolling back changes: {e}")
            raise
    
    def close(self):
        """Close the database session"""
        try:
            self.db.close()
        except SQLAlchemyError as e:
            logger.error(f"Error closing session: {e}")
            raise