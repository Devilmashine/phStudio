"""
Test suite for legal compliance features according to Russian legislation (152-ФЗ).
Tests consent management, cookie handling, and audit logging.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json

from app.models.consent import UserConsent
from app.models.legal_document import LegalDocument
from app.models.compliance_audit import ComplianceAuditLog
from app.services.consent_service import ConsentManagementService, CookieConsentService
from app.services.legal_document_service import LegalDocumentService


class TestCookieConsentCompliance:
    """Test cookie consent according to Russian legislation requirements"""

    def test_cookie_categories_available(self, client: AsyncClient):
        """Test that all required cookie categories are available"""
        response = client.get("/api/consent/cookie-consent/categories")
        assert response.status_code == 200
        
        categories = response.json()
        expected_categories = ["essential", "functional", "analytics", "marketing"]
        
        for category in expected_categories:
            assert category in categories
            assert "name" in categories[category]
            assert "description" in categories[category]
            assert "required" in categories[category]
        
        # Essential cookies must be required
        assert categories["essential"]["required"] is True

    def test_cookie_consent_recording(self, client: AsyncClient):
        """Test recording cookie consent with audit trail"""
        consent_data = {
            "accepted_categories": ["essential", "functional"]
        }
        
        response = client.post("/api/consent/cookie-consent/record", json=consent_data)
        assert response.status_code == 200
        
        result = response.json()
        assert result["consent_recorded"] is True
        assert "essential" in result["categories_accepted"]
        assert "functional" in result["categories_accepted"]
        assert result["consents_count"] == 2

    def test_cookie_consent_requires_essential(self, client: AsyncClient):
        """Test that essential cookies are always included"""
        consent_data = {
            "accepted_categories": ["functional"]  # Missing essential
        }
        
        response = client.post("/api/consent/cookie-consent/record", json=consent_data)
        assert response.status_code == 200
        
        result = response.json()
        assert "essential" in result["categories_accepted"]

    def test_invalid_cookie_categories_rejected(self, client: AsyncClient):
        """Test that invalid cookie categories are rejected"""
        consent_data = {
            "accepted_categories": ["invalid_category"]
        }
        
        response = client.post("/api/consent/cookie-consent/record", json=consent_data)
        assert response.status_code == 400


class TestBookingConsentCompliance:
    """Test booking consent compliance with 152-ФЗ"""

    def test_booking_consent_recording(self, client: AsyncClient):
        """Test that booking consent is properly recorded"""
        booking_data = {
            "client_name": "Иван Иванов",
            "client_phone": "+79991234567",
            "date": "2025-08-27",
            "times": ["10:00", "11:00"]
        }
        
        consent_request = {
            "booking_data": booking_data,
            "consent_versions": {
                "privacy": "1.0",
                "terms": "1.0"
            }
        }
        
        response = client.post("/api/consent/booking-consent/record", json=consent_request)
        assert response.status_code == 200
        
        result = response.json()
        assert result["consent_recorded"] is True
        assert "privacy" in result["consents"]
        assert "terms" in result["consents"]
        assert "audit_log_id" in result

    def test_booking_consent_with_ip_tracking(self, client: AsyncClient, db: Session):
        """Test that booking consent records IP address for audit trail"""
        booking_data = {
            "client_name": "Тест Тестов",
            "client_phone": "+79991234568",
            "date": "2025-08-27",
            "times": ["14:00"]
        }
        
        consent_request = {
            "booking_data": booking_data
        }
        
        # Set custom IP header
        headers = {"X-Forwarded-For": "192.168.1.100"}
        response = client.post(
            "/api/consent/booking-consent/record", 
            json=consent_request,
            headers=headers
        )
        assert response.status_code == 200
        
        # Verify IP address was recorded in audit log
        audit_logs = db.query(ComplianceAuditLog).filter(
            ComplianceAuditLog.event_type == "BOOKING_CONSENT_RECORDED"
        ).all()
        assert len(audit_logs) > 0
        
        latest_log = audit_logs[-1]
        assert str(latest_log.ip_address) == "192.168.1.100"


class TestConsentManagementService:
    """Test consent management service functionality"""

    def test_consent_withdrawal(self, db: Session):
        """Test consent withdrawal functionality"""
        service = ConsentManagementService(db)
        
        # First record a consent
        booking_data = {
            "id": 123,
            "client_phone": "+79991234569",
            "client_name": "Withdrawal Test"
        }
        
        result = service.record_booking_consent(
            booking_data=booking_data,
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            consent_versions={"privacy": "1.0", "terms": "1.0"}
        )
        
        assert result["consent_recorded"] is True
        
        # Then withdraw privacy consent
        user_identifier = f"booking_{booking_data['client_phone']}"
        withdrawal_result = service.withdraw_consent(
            user_identifier=user_identifier,
            consent_type="privacy",
            ip_address="192.168.1.1",
            user_agent="Test Browser"
        )
        
        assert withdrawal_result["consent_withdrawn"] is True
        assert withdrawal_result["consent_type"] == "privacy"

    def test_consent_summary(self, db: Session):
        """Test consent summary functionality"""
        service = ConsentManagementService(db)
        
        # Record some consents
        booking_data = {
            "id": 124,
            "client_phone": "+79991234570",
            "client_name": "Summary Test"
        }
        
        service.record_booking_consent(
            booking_data=booking_data,
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            consent_versions={"privacy": "1.0", "terms": "1.0"}
        )
        
        # Get summary
        user_identifier = f"booking_{booking_data['client_phone']}"
        summary = service.get_consent_summary(user_identifier)
        
        assert summary["user_identifier"] == user_identifier
        assert "privacy" in summary["consent_status"]
        assert "terms" in summary["consent_status"]
        assert summary["consent_status"]["privacy"]["given"] is True
        assert summary["consent_status"]["terms"]["given"] is True


class TestLegalDocumentManagement:
    """Test legal document management system"""

    def test_create_legal_document(self, client: AsyncClient, admin_token: str):
        """Test creating a new legal document version"""
        document_data = {
            "document_type": "privacy_policy",
            "title": "Test Privacy Policy",
            "content": "# Test Privacy Policy\n\nThis is a test policy.",
            "version": "2.0",
            "effective_date": datetime.now(timezone.utc).isoformat()
        }
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.post("/api/legal/documents", json=document_data, headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["document_type"] == "privacy_policy"
        assert result["version"] == "2.0"
        assert result["is_active"] is True
        assert result["hash_signature"] is not None

    def test_get_current_document(self, client: AsyncClient):
        """Test retrieving current active document"""
        response = client.get("/api/legal/documents/privacy_policy/current")
        
        if response.status_code == 200:
            result = response.json()
            assert result["document_type"] == "privacy_policy"
            assert result["is_active"] is True
        else:
            # If no document exists, it should return 404
            assert response.status_code == 404

    def test_document_versioning(self, client: AsyncClient, admin_token: str):
        """Test document versioning system"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create first version
        document_data_v1 = {
            "document_type": "terms_of_service",
            "title": "Terms v1",
            "content": "Terms version 1",
            "version": "1.0",
            "effective_date": datetime.now(timezone.utc).isoformat()
        }
        
        response = client.post("/api/legal/documents", json=document_data_v1, headers=headers)
        assert response.status_code == 200
        
        # Create second version
        document_data_v2 = {
            "document_type": "terms_of_service",
            "title": "Terms v2",
            "content": "Terms version 2",
            "version": "2.0",
            "effective_date": datetime.now(timezone.utc).isoformat()
        }
        
        response = client.post("/api/legal/documents", json=document_data_v2, headers=headers)
        assert response.status_code == 200
        
        # Check that only v2 is active
        response = client.get("/api/legal/documents/terms_of_service/current")
        assert response.status_code == 200
        
        result = response.json()
        assert result["version"] == "2.0"
        assert result["is_active"] is True
        
        # Check version history
        response = client.get("/api/legal/documents/terms_of_service/history")
        assert response.status_code == 200
        
        history = response.json()
        assert history["total_versions"] == 2
        assert len(history["versions"]) == 2

    def test_document_integrity_verification(self, client: AsyncClient, admin_token: str, db: Session):
        """Test document integrity verification using hash"""
        # First create a document
        service = LegalDocumentService(db)
        document = service.create_document(
            document_type="cookie_policy",
            title="Test Cookie Policy",
            content="Test content for integrity check",
            version="1.0",
            effective_date=datetime.now(timezone.utc),
            created_by=1
        )
        
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(f"/api/legal/documents/{document.id}/integrity", headers=headers)
        assert response.status_code == 200
        
        result = response.json()
        assert result["document_id"] == document.id
        assert result["integrity_verified"] is True
        assert result["stored_hash"] == result["calculated_hash"]


class TestAuditLoggingCompliance:
    """Test audit logging for legal compliance"""

    def test_audit_log_creation(self, db: Session):
        """Test that audit logs are created for compliance events"""
        # Create an audit log entry
        audit_log = ComplianceAuditLog(
            event_type="TEST_EVENT",
            user_identifier="test_user",
            ip_address="192.168.1.1",
            user_agent="Test Agent",
            action_details={
                "test_action": "test_value",
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            document_versions={"privacy": "1.0"}
        )
        
        db.add(audit_log)
        db.commit()
        
        # Verify the log was created
        retrieved_log = db.query(ComplianceAuditLog).filter(
            ComplianceAuditLog.event_type == "TEST_EVENT"
        ).first()
        
        assert retrieved_log is not None
        assert retrieved_log.user_identifier == "test_user"
        assert retrieved_log.action_details["test_action"] == "test_value"
        assert retrieved_log.retention_until is not None

    def test_audit_log_retention(self, db: Session):
        """Test that audit logs have proper retention periods"""
        service = ConsentManagementService(db)
        
        booking_data = {
            "id": 125,
            "client_phone": "+79991234571",
            "client_name": "Retention Test"
        }
        
        service.record_booking_consent(
            booking_data=booking_data,
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            consent_versions={"privacy": "1.0", "terms": "1.0"}
        )
        
        # Check that audit log has retention period set
        audit_log = db.query(ComplianceAuditLog).filter(
            ComplianceAuditLog.event_type == "BOOKING_CONSENT_RECORDED"
        ).order_by(ComplianceAuditLog.timestamp.desc()).first()
        
        assert audit_log is not None
        assert audit_log.retention_until is not None
        
        # Should be approximately 7 years in the future (2555 days)
        retention_period = audit_log.retention_until - audit_log.timestamp
        assert retention_period.days >= 2550  # Allow some tolerance


class TestComplianceIntegration:
    """Integration tests for complete compliance flow"""

    def test_complete_booking_with_consent_flow(self, client: AsyncClient):
        """Test complete booking flow with consent recording"""
        # First record cookie consent
        cookie_consent = {
            "accepted_categories": ["essential", "functional", "analytics"]
        }
        
        response = client.post("/api/consent/cookie-consent/record", json=cookie_consent)
        assert response.status_code == 200
        
        # Then record booking consent
        booking_data = {
            "client_name": "Integration Test User",
            "client_phone": "+79991234572",
            "date": "2025-08-27",
            "times": ["16:00"]
        }
        
        booking_consent = {
            "booking_data": booking_data
        }
        
        response = client.post("/api/consent/booking-consent/record", json=booking_consent)
        assert response.status_code == 200
        
        result = response.json()
        assert result["consent_recorded"] is True

    def test_gdpr_compliance_data_export(self, client: AsyncClient, db: Session):
        """Test data export functionality for GDPR compliance"""
        # Record some test data
        service = ConsentManagementService(db)
        user_identifier = "gdpr_test_user"
        
        # Record consents
        service.record_cookie_consent(
            ip_address="192.168.1.1",
            user_agent="Test Browser",
            accepted_categories=["essential", "functional"],
            user_identifier=user_identifier
        )
        
        # Get user consents (simulating data export)
        response = client.get(f"/api/consent/consent/user/{user_identifier}")
        assert response.status_code == 200
        
        result = response.json()
        assert result["user_identifier"] == user_identifier
        assert len(result["consents"]) > 0
        
        # Verify consent data includes all required fields
        for consent in result["consents"]:
            assert "consent_type" in consent
            assert "consent_given" in consent
            assert "consent_timestamp" in consent
            assert "consent_version" in consent
            assert "legal_basis" in consent


# Fixtures for admin token
@pytest.fixture
def admin_token():
    """Mock admin token for testing"""
    return "mock_admin_token"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])