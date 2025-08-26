from sqlalchemy import Column, Integer, String, DateTime, Text, Index, JSON
from sqlalchemy.dialects.postgresql import INET
from datetime import datetime, timezone, timedelta
from .base import Base


class ComplianceAuditLog(Base):
    """
    Enhanced audit logging for legal compliance with Russian legislation.
    Tracks all user actions with detailed context for 152-ФЗ compliance.
    """
    __tablename__ = "compliance_audit_logs"
    __table_args__ = (
        Index("idx_audit_logs_event_type", "event_type"),
        Index("idx_audit_logs_user", "user_identifier"),
        Index("idx_audit_logs_timestamp", "timestamp"),
        Index("idx_audit_logs_ip", "ip_address"),
        Index("idx_audit_logs_retention", "retention_until"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Type of event: 'BOOKING_CONSENT_RECORDED', 'COOKIE_CONSENT_RECORDED', 'LOGIN', 'DATA_ACCESS', etc.
    event_type = Column(String(100), nullable=False)
    
    # User identifier (can be phone, session ID, or IP for anonymous users)
    user_identifier = Column(String(255), nullable=True)
    
    # Client IP address
    ip_address = Column(INET, nullable=False)
    
    # User agent string
    user_agent = Column(Text, nullable=True)
    
    # Detailed action information as JSON
    action_details = Column(JSON, nullable=False)
    
    # When the action occurred
    timestamp = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # When this log entry should be deleted (legal retention requirements)
    # Default: 7 years for personal data operations
    retention_until = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc) + timedelta(days=2555),  # 7 years
        nullable=True
    )
    
    # Track which document versions were active at the time of action
    document_versions = Column(JSON, nullable=True)