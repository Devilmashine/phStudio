"""
Consent Management Service for Legal Compliance (152-ФЗ).
Handles user consent collection, tracking, and audit trail.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from app.models.consent import UserConsent
from app.models.compliance_audit import ComplianceAuditLog
from app.models.legal_document import LegalDocument
from app.core.database import get_db


class ConsentManagementService:
    """Manages user consent collection with legal compliance"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_booking_consent(
        self,
        booking_data: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        consent_versions: Dict[str, str]
    ) -> Dict[str, Any]:
        """Record all required consents for booking with audit trail"""
        
        user_identifier = f"booking_{booking_data['client_phone']}"
        
        # Record privacy consent (required)
        privacy_consent = UserConsent(
            user_identifier=user_identifier,
            consent_type="privacy",
            consent_given=True,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_version=consent_versions.get("privacy", "1.0"),
            legal_basis="contract_performance"
        )
        
        # Record terms acceptance (required)
        terms_consent = UserConsent(
            user_identifier=user_identifier,
            consent_type="terms",
            consent_given=True,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_version=consent_versions.get("terms", "1.0"),
            legal_basis="contract_performance"
        )
        
        self.db.add_all([privacy_consent, terms_consent])
        
        # Create compliance audit log
        audit_log = ComplianceAuditLog(
            event_type="BOOKING_CONSENT_RECORDED",
            user_identifier=user_identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            action_details={
                "booking_id": booking_data.get("id"),
                "consents_recorded": ["privacy", "terms"],
                "consent_versions": consent_versions,
                "data_collected": ["client_name", "client_phone"],
                "legal_basis": "contract_performance"
            },
            document_versions=consent_versions,
            retention_until=datetime.now(timezone.utc) + timedelta(days=2555)  # 7 years
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return {
            "consent_recorded": True,
            "consents": ["privacy", "terms"],
            "audit_log_id": audit_log.id
        }
    
    def record_cookie_consent(
        self,
        ip_address: str,
        user_agent: str,
        accepted_categories: List[str],
        user_identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record cookie consent with category breakdown"""
        
        if not user_identifier:
            user_identifier = f"cookie_{ip_address}"
        
        consents = []
        for category in accepted_categories:
            consent = UserConsent(
                user_identifier=user_identifier,
                consent_type=f"cookie_{category}",
                consent_given=True,
                ip_address=ip_address,
                user_agent=user_agent,
                consent_version="1.0",
                legal_basis="consent"
            )
            consents.append(consent)
            self.db.add(consent)
        
        # Log for compliance
        audit_log = ComplianceAuditLog(
            event_type="COOKIE_CONSENT_RECORDED",
            user_identifier=user_identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            action_details={
                "accepted_categories": accepted_categories,
                "all_categories": ["essential", "functional", "analytics", "marketing"],
                "consent_method": "banner_interaction"
            }
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return {
            "categories_accepted": accepted_categories,
            "consent_recorded": True,
            "consents_count": len(consents)
        }
    
    def get_user_consents(
        self,
        user_identifier: str,
        consent_type: Optional[str] = None
    ) -> List[UserConsent]:
        """Get all consents for a user, optionally filtered by type"""
        
        query = self.db.query(UserConsent).filter(
            UserConsent.user_identifier == user_identifier
        )
        
        if consent_type:
            query = query.filter(UserConsent.consent_type == consent_type)
        
        return query.order_by(desc(UserConsent.consent_timestamp)).all()
    
    def withdraw_consent(
        self,
        user_identifier: str,
        consent_type: str,
        ip_address: str,
        user_agent: str
    ) -> Dict[str, Any]:
        """Withdraw a specific consent type"""
        
        # Find the most recent active consent
        active_consent = self.db.query(UserConsent).filter(
            and_(
                UserConsent.user_identifier == user_identifier,
                UserConsent.consent_type == consent_type,
                UserConsent.consent_given == True,
                UserConsent.withdrawal_timestamp.is_(None)
            )
        ).order_by(desc(UserConsent.consent_timestamp)).first()
        
        if not active_consent:
            return {"error": "No active consent found to withdraw"}
        
        # Mark as withdrawn
        active_consent.withdrawal_timestamp = datetime.now(timezone.utc)
        
        # Create new withdrawal record
        withdrawal_consent = UserConsent(
            user_identifier=user_identifier,
            consent_type=consent_type,
            consent_given=False,
            ip_address=ip_address,
            user_agent=user_agent,
            consent_version=active_consent.consent_version,
            legal_basis=active_consent.legal_basis
        )
        
        self.db.add(withdrawal_consent)
        
        # Create audit log
        audit_log = ComplianceAuditLog(
            event_type="CONSENT_WITHDRAWN",
            user_identifier=user_identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            action_details={
                "consent_type": consent_type,
                "original_consent_id": active_consent.id,
                "withdrawal_method": "user_request"
            }
        )
        
        self.db.add(audit_log)
        self.db.commit()
        
        return {
            "consent_withdrawn": True,
            "consent_type": consent_type,
            "withdrawal_id": withdrawal_consent.id
        }
    
    def get_consent_summary(self, user_identifier: str) -> Dict[str, Any]:
        """Get a summary of all consents for a user"""
        
        all_consents = self.get_user_consents(user_identifier)
        
        # Group by consent type and get the latest status
        consent_status = {}
        for consent in all_consents:
            if consent.consent_type not in consent_status:
                consent_status[consent.consent_type] = {
                    "given": consent.consent_given,
                    "version": consent.consent_version,
                    "timestamp": consent.consent_timestamp,
                    "withdrawal_timestamp": consent.withdrawal_timestamp
                }
        
        return {
            "user_identifier": user_identifier,
            "consent_status": consent_status,
            "total_consents": len(all_consents)
        }


class CookieConsentService:
    """Specialized service for cookie consent management"""
    
    COOKIE_CATEGORIES = {
        "essential": {
            "name": "Необходимые",
            "description": "Обеспечивают базовую функциональность сайта",
            "required": True
        },
        "functional": {
            "name": "Функциональные", 
            "description": "Запоминают настройки и предпочтения",
            "required": False
        },
        "analytics": {
            "name": "Аналитические",
            "description": "Помогают анализировать использование сайта",
            "required": False
        },
        "marketing": {
            "name": "Маркетинговые",
            "description": "Используются для показа релевантной рекламы",
            "required": False
        }
    }
    
    def __init__(self, db: Session):
        self.db = db
        self.consent_service = ConsentManagementService(db)
    
    def get_cookie_categories(self) -> Dict[str, Dict[str, Any]]:
        """Get all available cookie categories"""
        return self.COOKIE_CATEGORIES
    
    def record_consent(
        self,
        ip_address: str,
        user_agent: str,
        accepted_categories: List[str]
    ) -> Dict[str, Any]:
        """Record cookie consent with validation"""
        
        # Validate categories
        valid_categories = set(self.COOKIE_CATEGORIES.keys())
        invalid_categories = set(accepted_categories) - valid_categories
        
        if invalid_categories:
            return {
                "error": f"Invalid categories: {list(invalid_categories)}",
                "valid_categories": list(valid_categories)
            }
        
        # Essential cookies are always required
        if "essential" not in accepted_categories:
            accepted_categories.append("essential")
        
        return self.consent_service.record_cookie_consent(
            ip_address=ip_address,
            user_agent=user_agent,
            accepted_categories=accepted_categories
        )
    
    def get_user_cookie_preferences(self, user_identifier: str) -> Dict[str, bool]:
        """Get current cookie preferences for a user"""
        
        preferences = {}
        for category in self.COOKIE_CATEGORIES.keys():
            # Get latest consent for this category
            consents = self.consent_service.get_user_consents(
                user_identifier=user_identifier,
                consent_type=f"cookie_{category}"
            )
            
            if consents:
                preferences[category] = consents[0].consent_given
            else:
                preferences[category] = False
        
        return preferences