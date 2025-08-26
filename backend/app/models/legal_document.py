from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base import Base


class LegalDocument(Base):
    """
    Legal document management model for versioning and tracking legal documents.
    Supports privacy policies, terms of service, cookie policies, etc.
    """
    __tablename__ = "legal_documents"
    __table_args__ = (
        Index("idx_legal_documents_type", "document_type"),
        Index("idx_legal_documents_version", "version"),
        Index("idx_legal_documents_active", "is_active"),
        Index("idx_legal_documents_effective", "effective_date"),
        {"extend_existing": True}
    )

    id = Column(Integer, primary_key=True, index=True)
    
    # Document type: 'privacy_policy', 'terms_of_service', 'cookie_policy', 'public_offer'
    document_type = Column(String(50), nullable=False)
    
    # Document version (e.g., "1.0", "2.1", etc.)
    version = Column(String(20), nullable=False)
    
    # Document title
    title = Column(Text, nullable=False)
    
    # Document content in markdown or HTML
    content = Column(Text, nullable=False)
    
    # When document was published/created
    published_date = Column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    
    # When document becomes effective (may be future date)
    effective_date = Column(DateTime(timezone=True), nullable=False)
    
    # Whether this version is currently active
    is_active = Column(Boolean, default=False, nullable=False)
    
    # User who created/published this version
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Hash signature for document integrity verification
    hash_signature = Column(String(255), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[created_by])