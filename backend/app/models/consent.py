from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import INET
from datetime import datetime, timezone
from .base import Base


class UserConsent(Base):
    """
    User consent tracking model for legal compliance (152-ФЗ).
    Tracks all types of consents including privacy, terms, cookies, and marketing.
    """
    __tablename__ = "user_consents"
    __table_args__ = (
        Index("idx_user_consents_identifier", "user_identifier"),
        Index("idx_user_consents_type", "consent_type"),
        Index("idx_user_consents_timestamp", "consent_timestamp"),
        Index("idx_user_consents_ip", "ip_address"),
        Index("idx_user_consents_active", "consent_given"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # User identification (can be IP, session ID, or phone for anonymous users)
    user_identifier = Column(String(255), nullable=False)
    
    # Consent type: 'privacy', 'terms', 'cookies', 'marketing', 'cookie_essential', 'cookie_functional', etc.
    consent_type = Column(String(50), nullable=False)
    
    # Whether consent was given or withdrawn
    consent_given = Column(Boolean, nullable=False)
    
    # When consent was recorded
    consent_timestamp = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # Client IP address for audit trail
    ip_address = Column(INET, nullable=False)
    
    # User agent for additional tracking
    user_agent = Column(Text, nullable=True)
    
    # Version of the document that was accepted
    consent_version = Column(String(50), nullable=False)
    
    # When consent was withdrawn (if applicable)
    withdrawal_timestamp = Column(DateTime(timezone=True), nullable=True)
    
    # Legal basis for processing: 'consent', 'contract_performance', 'legitimate_interest'
    legal_basis = Column(String(100), nullable=False, default='consent')
    
    # Record creation timestamp
    created_at = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )