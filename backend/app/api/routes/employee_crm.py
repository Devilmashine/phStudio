"""Employee CRM API routes.

Exposes read-only endpoints that surface aggregated metrics for the
Employee CRM dashboard extension without touching legacy endpoints.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.result import DomainError
from app.schemas.crm import CRMDashboardResponse
from app.services.employee_crm_service import EmployeeCRMService

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/crm", tags=["crm"])


class CRMEnvelope(BaseModel):
    """Standard response envelope for CRM endpoints."""

    success: bool
    data: CRMDashboardResponse
    message: str | None = None


@router.get("/dashboard", response_model=CRMEnvelope, summary="CRM dashboard metrics")
def get_employee_crm_dashboard(db: Session = Depends(get_db)) -> CRMEnvelope:
    """Provide aggregated CRM dashboard metrics."""

    service = EmployeeCRMService(db)
    result = service.get_dashboard()

    if result.is_failure():
        error = result.error()
        detail = error.to_dict() if isinstance(error, DomainError) else {"error": str(error)}
        logger.error("CRM dashboard generation failed", extra={"detail": detail})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )

    return CRMEnvelope(success=True, data=result.value(), message="CRM metrics generated")
