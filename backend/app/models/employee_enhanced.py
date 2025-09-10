"""
Enhanced Employee model with comprehensive security features.

This module provides a production-grade employee model that includes:
- Multi-factor authentication (MFA) support
- Role-based access control (RBAC)
- Account locking and rate limiting
- Password security features
- Session management
"""

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text, 
    ForeignKey, Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import ENUM as SAEnum
from sqlalchemy.sql import func

from .base_enhanced import BaseEnhanced
from .compliance_audit import ComplianceAuditLog


class EmployeeRole(str, PyEnum):
    """Employee roles with hierarchical permissions."""
    OWNER = "owner"      # Full system access
    ADMIN = "admin"      # Administrative access
    MANAGER = "manager"  # Operational access
    STAFF = "staff"      # Basic access
    VIEWER = "viewer"    # Read-only access


class EmployeeStatus(str, PyEnum):
    """Employee account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"
    PENDING_ACTIVATION = "pending_activation"


class Employee(BaseEnhanced):
    """
    Enhanced Employee model with comprehensive security features.
    
    This model implements enterprise-grade security following OWASP guidelines
    and provides a solid foundation for role-based access control.
    """
    
    __tablename__ = "employees"
    
    # Employee identification
    employee_id: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True,
        comment="Internal employee ID (e.g., EMP001)"
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    
    # Security fields
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Argon2 password hash"
    )
    
    role: Mapped[EmployeeRole] = mapped_column(
        SAEnum(EmployeeRole),
        nullable=False,
        default=EmployeeRole.STAFF,
        index=True
    )
    
    status: Mapped[EmployeeStatus] = mapped_column(
        SAEnum(EmployeeStatus),
        nullable=False,
        default=EmployeeStatus.PENDING_ACTIVATION,
        index=True
    )
    
    # MFA support
    mfa_secret: Mapped[Optional[str]] = mapped_column(
        String(32),
        nullable=True,
        comment="TOTP secret for MFA"
    )
    
    mfa_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )
    
    mfa_backup_codes: Mapped[Optional[List[str]]] = mapped_column(
        Text,  # JSON array stored as text
        nullable=True,
        comment="Backup codes for MFA recovery"
    )
    
    # Password security
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    password_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    password_history: Mapped[Optional[List[str]]] = mapped_column(
        Text,  # JSON array stored as text
        nullable=True,
        comment="Last 5 password hashes to prevent reuse"
    )
    
    # Account security
    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )
    
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    last_activity: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    
    last_password_reset: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Profile information
    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )
    
    phone: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        index=True
    )
    
    department: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )
    
    position: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True
    )
    
    hire_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Preferences and settings
    timezone: Mapped[Optional[str]] = mapped_column(
        String(50),
        default="UTC",
        nullable=False
    )
    
    language: Mapped[Optional[str]] = mapped_column(
        String(10),
        default="en",
        nullable=False
    )
    
    notification_preferences: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        Text,  # JSON stored as text
        nullable=True
    )
    
    # Relationships
    sessions: Mapped[List["EmployeeSession"]] = relationship(
        "EmployeeSession",
        back_populates="employee",
        cascade="all, delete-orphan",
        foreign_keys="EmployeeSession.employee_id"
    )
    
    # audit_logs: Mapped[List["ComplianceAuditLog"]] = relationship(
    #     "ComplianceAuditLog",
    #     foreign_keys="ComplianceAuditLog.employee_id",
    #     back_populates="employee"
    # )
    
    created_bookings: Mapped[List["Booking"]] = relationship(
        "app.models.booking_enhanced.Booking",
        foreign_keys="Booking.created_by",
        back_populates="created_by_employee"
    )
    
    updated_bookings: Mapped[List["Booking"]] = relationship(
        "app.models.booking_enhanced.Booking",
        foreign_keys="Booking.updated_by",
        back_populates="updated_by_employee"
    )
    
    # Table configuration
    __table_args__ = (
        # Composite indexes for common query patterns
        Index("idx_employee_role_status", "role", "status"),
        Index("idx_employee_department_status", "department", "status"),
        Index("idx_employee_last_activity", "last_activity"),
        Index("idx_employee_failed_logins", "failed_login_attempts", "locked_until"),
        
        # Check constraints
        CheckConstraint(
            "failed_login_attempts >= 0",
            name="check_failed_logins_non_negative"
        ),
        CheckConstraint(
            "LENGTH(username) >= 3",
            name="check_username_min_length"
        ),
        CheckConstraint(
            "LENGTH(password_hash) >= 32",
            name="check_password_hash_min_length"
        ),
        
        # Unique constraints
        UniqueConstraint("employee_id", name="uq_employee_id"),
        UniqueConstraint("username", name="uq_username"),
        UniqueConstraint("email", name="uq_email"),
        
        # Extend existing table configuration
        {"extend_existing": True}
    )
    
    def __init__(self, **kwargs):
        """Initialize the employee with security defaults."""
        # Set security defaults
        if "status" not in kwargs:
            kwargs["status"] = EmployeeStatus.PENDING_ACTIVATION
        if "mfa_enabled" not in kwargs:
            kwargs["mfa_enabled"] = False
        if "failed_login_attempts" not in kwargs:
            kwargs["failed_login_attempts"] = 0
        if "timezone" not in kwargs:
            kwargs["timezone"] = "UTC"
        if "language" not in kwargs:
            kwargs["language"] = "en"
        
        super().__init__(**kwargs)
    
    # Security methods
    def is_account_locked(self) -> bool:
        """Check if the account is currently locked."""
        if self.locked_until is None:
            return False
        return datetime.now(timezone.utc) < self.locked_until
    
    def is_password_expired(self) -> bool:
        """Check if the password has expired."""
        if self.password_expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.password_expires_at
    
    def is_password_change_required(self) -> bool:
        """Check if password change is required."""
        if self.password_changed_at is None:
            return True
        
        # Require password change every 90 days
        max_age = timedelta(days=90)
        return datetime.now(timezone.utc) - self.password_changed_at > max_age
    
    def can_login(self) -> bool:
        """Check if the employee can currently log in."""
        return (
            self.status == EmployeeStatus.ACTIVE and
            not self.is_account_locked() and
            not self.is_deleted
        )
    
    def record_failed_login(self) -> None:
        """Record a failed login attempt."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account(minutes=30)
        
        # Update audit trail
        self.update_audit_trail(
            "failed_login",
            user_id=0,  # System action
            details={"attempts": self.failed_login_attempts}
        )
    
    def record_successful_login(self) -> None:
        """Record a successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_login = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        
        # Update audit trail
        self.update_audit_trail(
            "successful_login",
            user_id=0,  # System action
            details={"ip_address": "unknown"}
        )
    
    def lock_account(self, minutes: int = 30) -> None:
        """Lock the account for a specified duration."""
        self.locked_until = datetime.now(timezone.utc) + timedelta(minutes=minutes)
        self.status = EmployeeStatus.LOCKED
        
        # Update audit trail
        self.update_audit_trail(
            "account_locked",
            user_id=0,  # System action
            details={"duration_minutes": minutes, "reason": "failed_logins"}
        )
    
    def unlock_account(self, user_id: int) -> None:
        """Unlock the account."""
        self.locked_until = None
        self.failed_login_attempts = 0
        self.status = EmployeeStatus.ACTIVE
        
        # Update audit trail
        self.update_audit_trail(
            "account_unlocked",
            user_id=user_id,
            details={"reason": "manual_unlock"}
        )
    
    def change_password(self, new_password_hash: str, user_id: int) -> None:
        """Change the employee's password."""
        # Update password history
        if self.password_history is None:
            self.password_history = []
        
        # Parse existing history
        try:
            if isinstance(self.password_history, str):
                import json
                history = json.loads(self.password_history)
            else:
                history = self.password_history
        except (json.JSONDecodeError, TypeError):
            history = []
        
        # Add current password to history
        if self.password_hash:
            history.append(self.password_hash)
        
        # Keep only last 5 passwords
        if len(history) > 5:
            history = history[-5:]
        
        self.password_history = history
        self.password_hash = new_password_hash
        self.password_changed_at = datetime.now(timezone.utc)
        self.password_expires_at = datetime.now(timezone.utc) + timedelta(days=90)
        
        # Update audit trail
        self.update_audit_trail(
            "password_changed",
            user_id=user_id
        )
    
    def enable_mfa(self, secret: str, backup_codes: List[str], user_id: int) -> None:
        """Enable multi-factor authentication."""
        self.mfa_secret = secret
        self.mfa_enabled = True
        self.mfa_backup_codes = backup_codes
        
        # Update audit trail
        self.update_audit_trail(
            "mfa_enabled",
            user_id=user_id
        )
    
    def disable_mfa(self, user_id: int) -> None:
        """Disable multi-factor authentication."""
        self.mfa_secret = None
        self.mfa_enabled = False
        self.mfa_backup_codes = None
        
        # Update audit trail
        self.update_audit_trail(
            "mfa_disabled",
            user_id=user_id
        )
    
    def update_activity(self) -> None:
        """Update the last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
    
    def has_permission(self, permission: str) -> bool:
        """Check if the employee has a specific permission."""
        # Define permission hierarchy
        permissions = {
            EmployeeRole.OWNER: ["*"],  # All permissions
            EmployeeRole.ADMIN: [
                "user_management", "system_config", "audit_logs",
                "booking_management", "reports", "analytics"
            ],
            EmployeeRole.MANAGER: [
                "booking_management", "staff_management", "reports",
                "calendar_management", "client_management"
            ],
            EmployeeRole.STAFF: [
                "booking_management", "calendar_view", "client_view",
                "basic_reports"
            ],
            EmployeeRole.VIEWER: [
                "calendar_view", "client_view", "basic_reports"
            ]
        }
        
        role_permissions = permissions.get(self.role, [])
        return "*" in role_permissions or permission in role_permissions
    
    def can_manage_employee(self, target_employee: 'Employee') -> bool:
        """Check if this employee can manage the target employee."""
        if self.role == EmployeeRole.OWNER:
            return True
        
        if self.role == EmployeeRole.ADMIN:
            return target_employee.role not in [EmployeeRole.OWNER, EmployeeRole.ADMIN]
        
        if self.role == EmployeeRole.MANAGER:
            return target_employee.role in [EmployeeRole.STAFF, EmployeeRole.VIEWER]
        
        return False
    
    def to_dict(self, include_security: bool = False) -> Dict[str, Any]:
        """
        Convert employee to dictionary.
        
        Args:
            include_security: Whether to include security-sensitive fields
            
        Returns:
            Dictionary representation of the employee
        """
        result = super().to_dict()
        
        # Add employee-specific fields
        result.update({
            "employee_id": self.employee_id,
            "username": self.username,
            "email": self.email,
            "role": self.role.value,
            "status": self.status.value,
            "full_name": self.full_name,
            "phone": self.phone,
            "department": self.department,
            "position": self.position,
            "hire_date": self.hire_date.isoformat() if self.hire_date else None,
            "timezone": self.timezone,
            "language": self.language,
            "mfa_enabled": self.mfa_enabled,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        })
        
        if include_security:
            result.update({
                "password_changed_at": self.password_changed_at.isoformat() if self.password_changed_at else None,
                "password_expires_at": self.password_expires_at.isoformat() if self.password_expires_at else None,
                "failed_login_attempts": self.failed_login_attempts,
                "locked_until": self.locked_until.isoformat() if self.locked_until else None,
                "is_account_locked": self.is_account_locked(),
                "is_password_expired": self.is_password_expired(),
                "is_password_change_required": self.is_password_change_required(),
                "can_login": self.can_login(),
            })
        
        return result
    
    def to_public_dict(self) -> Dict[str, Any]:
        """Convert employee to public dictionary (no sensitive information)."""
        return {
            "id": self.id,
            "employee_id": self.employee_id,
            "full_name": self.full_name,
            "department": self.department,
            "position": self.position,
            "status": self.status.value,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
        }
    
    @classmethod
    def get_roles(cls) -> List[str]:
        """Get list of available employee roles."""
        return [role.value for role in EmployeeRole]
    
    @classmethod
    def get_statuses(cls) -> List[str]:
        """Get list of available employee statuses."""
        return [status.value for status in EmployeeStatus]


# Employee Session model for tracking active sessions
class EmployeeSession(BaseEnhanced):
    """Model for tracking employee sessions."""
    
    __tablename__ = "employee_sessions"
    
    # Session identification
    session_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True
    )
    
    refresh_token: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )
    
    # Session details
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),  # IPv6 compatible
        nullable=True
    )
    
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )
    
    # Relationships
    employee_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    employee: Mapped[Employee] = relationship(
        "Employee",
        back_populates="sessions",
        foreign_keys=[employee_id]
    )
    
    # Table configuration
    __table_args__ = (
        Index("idx_session_employee_active", "employee_id", "is_active"),
        Index("idx_session_expires", "expires_at"),
        {"extend_existing": True}
    )
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.now(timezone.utc) > self.expires_at
    
    def deactivate(self) -> None:
        """Deactivate the session."""
        self.is_active = False
        self.updated_at = datetime.now(timezone.utc)
    
    def extend(self, additional_hours: int = 24) -> None:
        """Extend the session expiration."""
        self.expires_at += timedelta(hours=additional_hours)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        result = super().to_dict()
        result.update({
            "session_id": self.session_id,
            "employee_id": self.employee_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "expires_at": self.expires_at.isoformat(),
            "is_active": self.is_active,
            "is_expired": self.is_expired(),
        })
        return result