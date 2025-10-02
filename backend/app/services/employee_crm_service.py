"""Employee CRM service layer.

This module provides read-only aggregation helpers that power the
Employee CRM dashboard extension without mutating existing booking or employee
logic. The implementation leans on SQLAlchemy queries executed against
the enhanced models introduced for the CRM roadmap.
"""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List

import logging

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.core.result import DomainError, Result, failure, success
from app.models.booking_enhanced import Booking, BookingState
from app.models.employee_enhanced import Employee, EmployeeStatus
from app.schemas.crm import (
    CRMDashboardResponse,
    DashboardOverview,
    EmployeePerformance,
    PipelineStage,
    RevenuePoint,
)

logger = logging.getLogger(__name__)


class EmployeeCRMService:
    """Aggregates booking and employee data for CRM dashboards."""

    _ACTIVE_STATES = {
        BookingState.PENDING,
        BookingState.CONFIRMED,
        BookingState.IN_PROGRESS,
    }

    _PIPELINE_LABELS: Dict[BookingState, str] = {
        BookingState.PENDING: "Новые",
        BookingState.CONFIRMED: "Подтверждено",
        BookingState.IN_PROGRESS: "В работе",
        BookingState.COMPLETED: "Завершено",
        BookingState.CANCELLED: "Отменено",
        BookingState.NO_SHOW: "Неявка",
        BookingState.DRAFT: "Черновик",
        BookingState.RESCHEDULED: "Перенесено",
    }

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_dashboard(self) -> Result[CRMDashboardResponse, DomainError]:
        """Return aggregated metrics for the CRM dashboard."""

        try:
            now = datetime.now(timezone.utc)
            start_30_days = now - timedelta(days=30)
            start_7_days = now - timedelta(days=6)
            today = now.date()

            overview = self._build_overview(today, start_30_days)
            pipeline = self._build_pipeline(start_30_days)
            employees = self._build_employee_performance(start_30_days)
            revenue_trend = self._build_revenue_trend(start_7_days.date(), today)

            response = CRMDashboardResponse(
                overview=overview.model_dump(),
                pipeline=[stage.model_dump() for stage in pipeline],
                top_employees=[employee.model_dump() for employee in employees],
                revenue_trend=[point.model_dump() for point in revenue_trend],
                generated_at=now,
            )
            return success(response)

        except Exception as exc:  # pragma: no cover - defensive logging path
            logger.exception("Failed to build CRM dashboard")
            return failure(
                DomainError(
                    "Failed to build CRM dashboard",
                    code="CRM_DASHBOARD_ERROR",
                    details={"error": str(exc)},
                )
            )

    def _build_overview(self, today: date, start_30_days: datetime) -> DashboardOverview:
        total_bookings = (
            self.db.query(func.count(Booking.id))
            .filter(
                Booking.is_deleted.is_(False),
                Booking.booking_date >= start_30_days.date(),
            )
            .scalar()
            or 0
        )

        active_bookings = (
            self.db.query(func.count(Booking.id))
            .filter(
                Booking.is_deleted.is_(False),
                Booking.state.in_(list(self._ACTIVE_STATES)),
            )
            .scalar()
            or 0
        )

        completed_today = (
            self.db.query(func.count(Booking.id))
            .filter(
                Booking.is_deleted.is_(False),
                Booking.state == BookingState.COMPLETED,
                Booking.booking_date == today,
            )
            .scalar()
            or 0
        )

        revenue_30_days = (
            self.db.query(
                func.coalesce(
                    func.sum(
                        case(
                            (Booking.state.in_([BookingState.COMPLETED, BookingState.CONFIRMED]), Booking.total_price),
                            else_=0,
                        )
                    ),
                    0,
                )
            )
            .filter(
                Booking.is_deleted.is_(False),
                Booking.booking_date >= start_30_days.date(),
            )
            .scalar()
            or 0
        )

        completed_bookings_count = (
            self.db.query(func.count(Booking.id))
            .filter(
                Booking.is_deleted.is_(False),
                Booking.state == BookingState.COMPLETED,
                Booking.booking_date >= start_30_days.date(),
            )
            .scalar()
            or 0
        )

        average_booking_value = (
            float(revenue_30_days) / completed_bookings_count
            if completed_bookings_count
            else 0.0
        )

        booked_hours = (
            self.db.query(
                func.coalesce(func.sum(Booking.duration_hours), 0)
            )
            .filter(
                Booking.is_deleted.is_(False),
                Booking.booking_date >= start_30_days.date(),
            )
            .scalar()
            or Decimal("0")
        )

        # Assume a conservative operational window of 12 hours per day
        # across three rooms to avoid overstating utilisation.
        capacity_hours = Decimal("36") * 30  # 3 rooms * 12h * 30 days
        occupancy_rate = (
            float(booked_hours) / float(capacity_hours) * 100
            if capacity_hours > 0
            else 0.0
        )

        return DashboardOverview(
            total_bookings=int(total_bookings),
            active_bookings=int(active_bookings),
            completed_today=int(completed_today),
            revenue_30_days=float(revenue_30_days),
            avg_booking_value=round(average_booking_value, 2),
            occupancy_rate=round(min(occupancy_rate, 100.0), 2),
        )

    def _build_pipeline(self, start_30_days: datetime) -> List[PipelineStage]:
        rows = (
            self.db.query(Booking.state, func.count(Booking.id))
            .filter(
                Booking.is_deleted.is_(False),
                Booking.booking_date >= start_30_days.date(),
            )
            .group_by(Booking.state)
            .all()
        )

        counts = {state: 0 for state in BookingState}
        for state, count in rows:
            counts[state] = int(count)

        total = sum(counts.values()) or 0

        pipeline: List[PipelineStage] = []
        # Desired order for kanban-style колонок
        ordered_states = [
            BookingState.PENDING,
            BookingState.CONFIRMED,
            BookingState.IN_PROGRESS,
            BookingState.COMPLETED,
            BookingState.CANCELLED,
            BookingState.NO_SHOW,
            BookingState.RESCHEDULED,
            BookingState.DRAFT,
        ]

        seen = set()
        for state in ordered_states + [s for s in BookingState if s not in ordered_states]:
            if state in seen:
                continue
            seen.add(state)
            count = counts.get(state, 0)
            percentage = round((count / total * 100) if total else 0.0, 2)
            pipeline.append(
                PipelineStage(
                    state=state,
                    label=self._PIPELINE_LABELS.get(state, state.value),
                    count=count,
                    percentage=percentage,
                )
            )

        return pipeline

    def _build_employee_performance(self, start_30_days: datetime) -> List[EmployeePerformance]:
        booking_join_condition = (
            (Booking.created_by == Employee.id)
            & (Booking.is_deleted.is_(False))
            & (Booking.booking_date >= start_30_days.date())
        )

        rows = (
            self.db.query(
                Employee.id.label("employee_id"),
                Employee.full_name,
                Employee.role,
                func.coalesce(
                    func.sum(
                        case((Booking.state == BookingState.COMPLETED, 1), else_=0)
                    ),
                    0,
                ).label("completed_count"),
                func.coalesce(
                    func.sum(
                        case((Booking.state.in_(list(self._ACTIVE_STATES)), 1), else_=0)
                    ),
                    0,
                ).label("active_count"),
                func.coalesce(
                    func.sum(
                        case(
                            (Booking.state == BookingState.COMPLETED, Booking.total_price),
                            else_=0,
                        )
                    ),
                    0,
                ).label("revenue_sum"),
            )
            .outerjoin(Booking, booking_join_condition)
            .filter(Employee.status == EmployeeStatus.ACTIVE)
            .group_by(Employee.id, Employee.full_name, Employee.role)
            .order_by(func.coalesce(func.sum(case((Booking.state == BookingState.COMPLETED, 1), else_=0)), 0).desc())
            .limit(5)
            .all()
        )

        performances: List[EmployeePerformance] = []
        performances: List[EmployeePerformance] = [
            EmployeePerformance(
                employee_id=row.employee_id,
                full_name=row.full_name,
                role=row.role.value if hasattr(row.role, "value") else row.role,
                completed_bookings=int(row.completed_count or 0),
                active_bookings=int(row.active_count or 0),
                revenue_generated=float(row.revenue_sum or 0),
            )
            for row in rows
        ]

        if performances:
            return performances

        # Fallback: отдать активных сотрудников без статистики
        fallback_employees = (
            self.db.query(Employee)
            .filter(Employee.status == EmployeeStatus.ACTIVE)
            .order_by(Employee.created_at.desc())
            .limit(5)
            .all()
        )

        return [
            EmployeePerformance(
                employee_id=emp.id,
                full_name=emp.full_name,
                role=emp.role.value if hasattr(emp.role, "value") else emp.role,
                completed_bookings=0,
                active_bookings=0,
                revenue_generated=0.0,
            )
            for emp in fallback_employees
        ]
    def _build_revenue_trend(self, start_day: date, end_day: date) -> List[RevenuePoint]:
        rows = (
            self.db.query(
                Booking.booking_date,
                func.coalesce(
                    func.sum(
                        case((Booking.state == BookingState.COMPLETED, Booking.total_price), else_=0)
                    ),
                    0,
                ).label("revenue"),
                func.coalesce(
                    func.sum(case((Booking.state == BookingState.COMPLETED, 1), else_=0)),
                    0,
                ).label("count"),
            )
            .filter(
                Booking.is_deleted.is_(False),
                Booking.booking_date >= start_day,
                Booking.booking_date <= end_day,
            )
            .group_by(Booking.booking_date)
            .order_by(Booking.booking_date)
            .all()
        )

        by_date = {row.booking_date: row for row in rows}
        trend: List[RevenuePoint] = []

        current = start_day
        while current <= end_day:
            data = by_date.get(current)
            revenue = float(data.revenue) if data else 0.0
            count = int(data.count) if data else 0
            trend.append(
                RevenuePoint(date=current, revenue=round(revenue, 2), booking_count=count)
            )
            current += timedelta(days=1)

        return trend
