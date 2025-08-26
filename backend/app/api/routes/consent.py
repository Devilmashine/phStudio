"""
Consent Management API Routes for Legal Compliance.
Handles user consent collection and tracking according to 152-ФЗ.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel, Field
import logging

from app.core.database import get_db
from app.services.consent_service import ConsentManagementService, CookieConsentService
from app.services.legal_document_service import LegalDocumentService
from app.api.routes.auth import get_client_ip

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models for request/response
class CookieConsentRequest(BaseModel):
    accepted_categories: List[str] = Field(..., description="List of accepted cookie categories")

class CookieConsentResponse(BaseModel):
    categories_accepted: List[str]
    consent_recorded: bool
    consents_count: int

class BookingConsentRequest(BaseModel):
    booking_data: Dict[str, Any]
    consent_versions: Dict[str, str] = Field(default_factory=dict)

class ConsentSummaryResponse(BaseModel):
    user_identifier: str
    consent_status: Dict[str, Any]
    total_consents: int

class ConsentWithdrawalRequest(BaseModel):
    user_identifier: str
    consent_type: str


@router.post("/cookie-consent/record", response_model=CookieConsentResponse)
async def record_cookie_consent(
    request: CookieConsentRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Record user's cookie consent preferences"""
    
    client_ip = get_client_ip(http_request)
    user_agent = http_request.headers.get("User-Agent", "")
    
    cookie_service = CookieConsentService(db)
    
    try:
        result = cookie_service.record_consent(
            ip_address=client_ip,
            user_agent=user_agent,
            accepted_categories=request.accepted_categories
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return CookieConsentResponse(**result)
        
    except Exception as e:
        logger.error(f"Failed to record cookie consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to record cookie consent")


@router.get("/cookie-consent/categories")
async def get_cookie_categories(db: Session = Depends(get_db)):
    """Get available cookie categories with descriptions"""
    
    cookie_service = CookieConsentService(db)
    return cookie_service.get_cookie_categories()


@router.get("/cookie-consent/preferences/{user_identifier}")
async def get_cookie_preferences(
    user_identifier: str,
    db: Session = Depends(get_db)
):
    """Get user's current cookie preferences"""
    
    cookie_service = CookieConsentService(db)
    preferences = cookie_service.get_user_cookie_preferences(user_identifier)
    
    return {
        "user_identifier": user_identifier,
        "preferences": preferences
    }


@router.post("/booking-consent/record")
async def record_booking_consent(
    request: BookingConsentRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Record consent for booking operations"""
    
    client_ip = get_client_ip(http_request)
    user_agent = http_request.headers.get("User-Agent", "")
    
    consent_service = ConsentManagementService(db)
    legal_service = LegalDocumentService(db)
    
    # Get current document versions if not provided
    if not request.consent_versions:
        request.consent_versions = legal_service.get_document_versions_for_consent()
    
    try:
        result = consent_service.record_booking_consent(
            booking_data=request.booking_data,
            ip_address=client_ip,
            user_agent=user_agent,
            consent_versions=request.consent_versions
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to record booking consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to record booking consent")


@router.get("/consent/summary/{user_identifier}", response_model=ConsentSummaryResponse)
async def get_consent_summary(
    user_identifier: str,
    db: Session = Depends(get_db)
):
    """Get summary of all consents for a user"""
    
    consent_service = ConsentManagementService(db)
    
    try:
        summary = consent_service.get_consent_summary(user_identifier)
        return ConsentSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Failed to get consent summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to get consent summary")


@router.post("/consent/withdraw")
async def withdraw_consent(
    request: ConsentWithdrawalRequest,
    http_request: Request,
    db: Session = Depends(get_db)
):
    """Withdraw a specific type of consent"""
    
    client_ip = get_client_ip(http_request)
    user_agent = http_request.headers.get("User-Agent", "")
    
    consent_service = ConsentManagementService(db)
    
    try:
        result = consent_service.withdraw_consent(
            user_identifier=request.user_identifier,
            consent_type=request.consent_type,
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to withdraw consent: {e}")
        raise HTTPException(status_code=500, detail="Failed to withdraw consent")


@router.get("/consent/user/{user_identifier}")
async def get_user_consents(
    user_identifier: str,
    consent_type: str = None,
    db: Session = Depends(get_db)
):
    """Get all consents for a specific user"""
    
    consent_service = ConsentManagementService(db)
    
    try:
        consents = consent_service.get_user_consents(
            user_identifier=user_identifier,
            consent_type=consent_type
        )
        
        return {
            "user_identifier": user_identifier,
            "consent_type_filter": consent_type,
            "consents": [
                {
                    "id": consent.id,
                    "consent_type": consent.consent_type,
                    "consent_given": consent.consent_given,
                    "consent_timestamp": consent.consent_timestamp,
                    "consent_version": consent.consent_version,
                    "legal_basis": consent.legal_basis,
                    "withdrawal_timestamp": consent.withdrawal_timestamp
                }
                for consent in consents
            ],
            "total_count": len(consents)
        }
        
    except Exception as e:
        logger.error(f"Failed to get user consents: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user consents")


# Health check endpoint for consent service
@router.get("/consent/health")
async def consent_service_health(db: Session = Depends(get_db)):
    """Health check for consent management service"""
    
    try:
        # Test database connection
        consent_service = ConsentManagementService(db)
        cookie_service = CookieConsentService(db)
        
        return {
            "status": "healthy",
            "services": {
                "consent_management": "operational",
                "cookie_consent": "operational",
                "database": "connected"
            },
            "cookie_categories": len(cookie_service.COOKIE_CATEGORIES)
        }
        
    except Exception as e:
        logger.error(f"Consent service health check failed: {e}")
        raise HTTPException(status_code=503, detail="Consent service unhealthy")