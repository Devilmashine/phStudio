"""
Enhanced base model with audit fields and optimistic locking.

This module provides a comprehensive base model that includes:
- Audit fields (created_at, updated_at, created_by, updated_by)
- Optimistic locking with version field
- Soft delete support
- Audit trail capabilities
"""

from datetime import datetime, timezone
from typing import Any, Dict, Optional
from sqlalchemy import (
    Column, Integer, DateTime, String, Boolean, Text, 
    ForeignKey, Index, CheckConstraint
)
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

from .base import Base


class BaseEnhanced(Base):
    """
    Enhanced base model with comprehensive audit and tracking capabilities.
    
    This model follows FAANG engineering standards for production systems
    and provides a solid foundation for all domain entities.
    """
    
    __abstract__ = True
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Audit fields
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    # User tracking
    created_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    updated_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Optimistic locking
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        index=True
    )
    
    # Soft delete support
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    deleted_by: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Audit trail
    audit_trail: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        Text,  # JSON stored as text for PostgreSQL compatibility
        nullable=True
    )
    
    # Metadata
    model_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        Text,  # JSON stored as text for PostgreSQL compatibility
        nullable=True
    )
    
    # Table configuration
    __table_args__ = (
        # Composite indexes for common query patterns
        Index("idx_created_at_created_by", "created_at", "created_by"),
        Index("idx_updated_at_updated_by", "updated_at", "updated_by"),
        Index("idx_version_updated_at", "version", "updated_at"),
        Index("idx_is_deleted_created_at", "is_deleted", "created_at"),
        
        # Check constraints
        CheckConstraint("version > 0", name="check_version_positive"),
        CheckConstraint(
            "(is_deleted = false AND deleted_at IS NULL AND deleted_by IS NULL) OR "
            "(is_deleted = true AND deleted_at IS NOT NULL)",
            name="check_soft_delete_consistency"
        ),
        
        # Extend existing table configuration
        {"extend_existing": True}
    )
    
    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower() + "s"
    
    def __init__(self, **kwargs):
        """Initialize the model with audit fields."""
        # Set audit fields if not provided
        if "created_at" not in kwargs:
            kwargs["created_at"] = datetime.now(timezone.utc)
        if "updated_at" not in kwargs:
            kwargs["updated_at"] = datetime.now(timezone.utc)
        if "version" not in kwargs:
            kwargs["version"] = 1
        if "is_deleted" not in kwargs:
            kwargs["is_deleted"] = False
        
        super().__init__(**kwargs)
    
    def update_audit_trail(self, action: str, user_id: int, details: Optional[Dict[str, Any]] = None) -> None:
        """
        Update audit trail with a new entry.
        
        Args:
            action: The action performed (e.g., 'created', 'updated', 'deleted')
            user_id: ID of the user who performed the action
            details: Additional details about the action
        """
        if self.audit_trail is None:
            self.audit_trail = {}
        
        # Parse existing audit trail
        try:
            if isinstance(self.audit_trail, str):
                import json
                trail = json.loads(self.audit_trail)
            else:
                trail = self.audit_trail
        except (json.JSONDecodeError, TypeError):
            trail = {}
        
        # Add new entry
        entry = {
            "action": action,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": self.version,
            "details": details or {}
        }
        
        # Ensure audit_trail is a list
        if not isinstance(trail, list):
            trail = []
        
        trail.append(entry)
        
        # Limit audit trail size to prevent excessive storage
        if len(trail) > 100:
            trail = trail[-100:]
        
        # Serialize to JSON string for database storage
        import json
        self.audit_trail = json.dumps(trail)
    
    def soft_delete(self, user_id: int, reason: Optional[str] = None) -> None:
        """
        Soft delete the entity.
        
        Args:
            user_id: ID of the user performing the deletion
            reason: Optional reason for deletion
        """
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        self.deleted_by = user_id
        
        # Update audit trail
        details = {"reason": reason} if reason else {}
        self.update_audit_trail("deleted", user_id, details)
        
        # Increment version for optimistic locking
        self.version += 1
    
    def restore(self, user_id: int) -> None:
        """
        Restore a soft-deleted entity.
        
        Args:
            user_id: ID of the user performing the restoration
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        
        # Update audit trail
        self.update_audit_trail("restored", user_id)
        
        # Increment version for optimistic locking
        self.version += 1
    
    def touch(self, user_id: int, reason: Optional[str] = None) -> None:
        """
        Update the entity without changing any fields (useful for keeping track of access).
        
        Args:
            user_id: ID of the user accessing the entity
            reason: Optional reason for the access
        """
        self.updated_at = datetime.now(timezone.utc)
        self.updated_by = user_id
        
        # Update audit trail
        details = {"reason": reason} if reason else {}
        self.update_audit_trail("accessed", user_id, details)
    
    def increment_version(self) -> None:
        """Increment the version for optimistic locking."""
        self.version += 1
    
    def to_dict(self, include_audit: bool = True, include_metadata: bool = True) -> Dict[str, Any]:
        """
        Convert entity to dictionary.
        
        Args:
            include_audit: Whether to include audit fields
            include_metadata: Whether to include metadata fields
            
        Returns:
            Dictionary representation of the entity
        """
        result = {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version,
            "is_deleted": self.is_deleted,
        }
        
        if include_audit:
            result.update({
                "created_by": self.created_by,
                "updated_by": self.updated_by,
                "deleted_at": self.deleted_at.isoformat() if self.deleted_at else None,
                "deleted_by": self.deleted_by,
                "audit_trail": self.audit_trail,
            })
        
        if include_metadata:
            result["metadata"] = self.model_metadata
        
        return result
    
    def to_audit_dict(self) -> Dict[str, Any]:
        """
        Convert entity to audit dictionary format.
        
        Returns:
            Dictionary suitable for audit logging
        """
        return {
            "entity_type": self.__class__.__name__,
            "entity_id": self.id,
            "action": "accessed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": self.version,
            "is_deleted": self.is_deleted,
            "audit_trail": self.audit_trail,
        }
    
    @classmethod
    def get_audit_fields(cls) -> list:
        """Get list of audit field names."""
        return [
            "created_at", "updated_at", "created_by", "updated_by",
            "version", "is_deleted", "deleted_at", "deleted_by",
            "audit_trail", "model_metadata"
        ]
    
    @classmethod
    def get_business_fields(cls) -> list:
        """Get list of business field names (excluding audit fields)."""
        audit_fields = set(cls.get_audit_fields())
        return [field for field in cls.__table__.columns.keys() if field not in audit_fields]


class TimestampedMixin:
    """
    Mixin for models that only need basic timestamp tracking.
    
    Use this when you don't need the full audit capabilities of BaseEnhanced.
    """
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )
    
    __table_args__ = (
        Index("idx_created_at", "created_at"),
        Index("idx_updated_at", "updated_at"),
        {"extend_existing": True}
    )


class SoftDeleteMixin:
    """
    Mixin for models that need soft delete functionality.
    
    Use this when you need soft delete but not the full audit capabilities.
    """
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    __table_args__ = (
        Index("idx_is_deleted", "is_deleted"),
        CheckConstraint(
            "(is_deleted = false AND deleted_at IS NULL) OR "
            "(is_deleted = true AND deleted_at IS NOT NULL)",
            name="check_soft_delete_consistency"
        ),
        {"extend_existing": True}
    )
    
    def soft_delete(self) -> None:
        """Soft delete the entity."""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
    
    def restore(self) -> None:
        """Restore a soft-deleted entity."""
        self.is_deleted = False
        self.deleted_at = None


class VersionedMixin:
    """
    Mixin for models that need optimistic locking.
    
    Use this when you need version tracking but not the full audit capabilities.
    """
    
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        index=True
    )
    
    __table_args__ = (
        Index("idx_version", "version"),
        CheckConstraint("version > 0", name="check_version_positive"),
        {"extend_existing": True}
    )
    
    def increment_version(self) -> None:
        """Increment the version for optimistic locking."""
        self.version += 1


# Utility functions for working with enhanced models
def create_audit_entry(
    action: str,
    user_id: int,
    details: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create a standardized audit entry.
    
    Args:
        action: The action performed
        user_id: ID of the user who performed the action
        details: Additional details about the action
        timestamp: When the action occurred (defaults to now)
        
    Returns:
        Dictionary representing the audit entry
    """
    return {
        "action": action,
        "user_id": user_id,
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
        "details": details or {}
    }


def merge_audit_trails(
    *trails: list,
    max_entries: int = 100
) -> list:
    """
    Merge multiple audit trails into one.
    
    Args:
        *trails: Variable number of audit trail lists
        max_entries: Maximum number of entries to keep
        
    Returns:
        Merged audit trail
    """
    merged = []
    
    for trail in trails:
        if isinstance(trail, list):
            merged.extend(trail)
    
    # Sort by timestamp (assuming ISO format)
    merged.sort(key=lambda x: x.get("timestamp", ""))
    
    # Limit size
    if len(merged) > max_entries:
        merged = merged[-max_entries:]
    
    return merged


def filter_audit_trail(
    trail: list,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list:
    """
    Filter audit trail by various criteria.
    
    Args:
        trail: The audit trail to filter
        action: Filter by specific action
        user_id: Filter by specific user
        start_date: Filter entries after this date
        end_date: Filter entries before this date
        
    Returns:
        Filtered audit trail
    """
    if not isinstance(trail, list):
        return []
    
    filtered = trail
    
    if action:
        filtered = [entry for entry in filtered if entry.get("action") == action]
    
    if user_id:
        filtered = [entry for entry in filtered if entry.get("user_id") == user_id]
    
    if start_date:
        filtered = [
            entry for entry in filtered
            if entry.get("timestamp") and datetime.fromisoformat(entry["timestamp"]) >= start_date
        ]
    
    if end_date:
        filtered = [
            entry for entry in filtered
            if entry.get("timestamp") and datetime.fromisoformat(entry["timestamp"]) <= end_date
        ]
    
    return filtered