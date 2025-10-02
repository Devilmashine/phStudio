"""
Employee CRM dashboard schemas.

These Pydantic models define the response structure for the
Employee CRM extension, providing aggregated metrics that power
the admin dashboards without altering legacy endpoints.
"""

import datetime as dt
from typing import List

from pydantic import BaseModel, Field

from app.models.booking_enhanced import BookingState


class PipelineStage(BaseModel):
    """Aggregated booking counts grouped by workflow state."""

    state: BookingState = Field(..., description="Booking state represented by the column")
    label: str = Field(..., description="Human readable column label")
    count: int = Field(..., ge=0, description="Number of bookings in this state")
    percentage: float = Field(
        ...,
        ge=0,
        le=100,
        description="Share of bookings in this state relative to all active bookings",
    )


class EmployeePerformance(BaseModel):
    """Service level indicators for individual employees."""

    employee_id: int = Field(..., description="Internal employee identifier")
    full_name: str = Field(..., description="Employee full name")
    role: str = Field(..., description="Employee role label")
    completed_bookings: int = Field(..., ge=0, description="Handled bookings completed in window")
    active_bookings: int = Field(..., ge=0, description="Open bookings currently assigned")
    revenue_generated: float = Field(
        ...,
        ge=0,
        description="Total revenue produced by the employee in analysis window",
    )


class RevenuePoint(BaseModel):
    """Daily revenue snapshot used for simple trend visualisation."""

    date: dt.date = Field(..., description="Date of aggregation (UTC)")
    revenue: float = Field(..., ge=0, description="Total revenue for the day")
    booking_count: int = Field(..., ge=0, description="Number of bookings contributing to revenue")


class DashboardOverview(BaseModel):
    """Headline metrics displayed on the CRM overview screen."""

    total_bookings: int = Field(..., ge=0, description="Total bookings recorded in the window")
    active_bookings: int = Field(..., ge=0, description="Bookings currently in progress pipeline")
    completed_today: int = Field(..., ge=0, description="Bookings completed during the current day")
    revenue_30_days: float = Field(..., ge=0, description="Revenue produced in the last 30 days")
    avg_booking_value: float = Field(..., ge=0, description="Average revenue per completed booking")
    occupancy_rate: float = Field(
        ...,
        ge=0,
        le=100,
        description="Utilisation percentage of booked hours versus capacity",
    )


class CRMDashboardResponse(BaseModel):
    """Composite payload consumed by the frontend CRM extension."""

    overview: DashboardOverview
    pipeline: List[PipelineStage]
    top_employees: List[EmployeePerformance]
    revenue_trend: List[RevenuePoint]
    generated_at: dt.datetime = Field(..., description="Timestamp when metrics were produced")
