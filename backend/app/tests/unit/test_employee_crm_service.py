import pytest
from unittest.mock import MagicMock

from backend.app.models.booking_enhanced import BookingState
from backend.app.schemas.crm import (
    CRMDashboardResponse,
    DashboardOverview,
    EmployeePerformance,
    PipelineStage,
    RevenuePoint,
)
from backend.app.services.employee_crm_service import EmployeeCRMService


class StubEmployeeCRMService(EmployeeCRMService):
    def __init__(self):
        super().__init__(db=MagicMock())

    def _build_overview(self, *_args, **_kwargs) -> DashboardOverview:  # type: ignore[override]
        return DashboardOverview(
            total_bookings=10,
            active_bookings=4,
            completed_today=2,
            revenue_30_days=15000.0,
            avg_booking_value=5000.0,
            occupancy_rate=67.0,
        )

    def _build_pipeline(self, *_args, **_kwargs):  # type: ignore[override]
        return [
            PipelineStage(
                state=BookingState.PENDING,
                label="Новые",
                count=3,
                percentage=30.0,
            ),
            PipelineStage(
                state=BookingState.COMPLETED,
                label="Завершено",
                count=7,
                percentage=70.0,
            ),
        ]

    def _build_employee_performance(self, *_args, **_kwargs):  # type: ignore[override]
        return [
            EmployeePerformance(
                employee_id=1,
                full_name="Алексей Иванов",
                role="manager",
                completed_bookings=5,
                active_bookings=1,
                revenue_generated=8500.0,
            )
        ]

    def _build_revenue_trend(self, *_args, **_kwargs):  # type: ignore[override]
        return [
            RevenuePoint(date=_date, revenue=2000.0, booking_count=1)
            for _date in (
                self._reference_date("2024-09-01"),
                self._reference_date("2024-09-02"),
            )
        ]

    @staticmethod
    def _reference_date(value: str):
        from datetime import datetime

        return datetime.fromisoformat(value).date()


def test_get_dashboard_returns_successful_result():
    service = StubEmployeeCRMService()

    result = service.get_dashboard()

    assert result.is_success()
    payload: CRMDashboardResponse = result.value()
    assert payload.overview.total_bookings == 10
    assert payload.pipeline[0].state == BookingState.PENDING
    assert payload.top_employees[0].full_name == "Алексей Иванов"
    assert payload.revenue_trend[0].revenue == 2000.0
    assert payload.generated_at is not None


def test_get_dashboard_handles_failure(monkeypatch):
    service = EmployeeCRMService(db=MagicMock())

    def boom(*_args, **_kwargs):
        raise RuntimeError("broken query")

    monkeypatch.setattr(service, "_build_overview", boom)

    result = service.get_dashboard()

    assert result.is_failure()
    error = result.error()
    assert hasattr(error, "code")
    assert getattr(error, "code") == "CRM_DASHBOARD_ERROR"
