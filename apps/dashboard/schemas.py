from datetime import datetime

from pydantic import BaseModel

from apps.requests.schemas import RequestStatus

# =====================================================
# Dashboard Schemas
# Pydantic models for admin and user dashboard responses.
# =====================================================


class AdminDashboardStatsResponse(BaseModel):
    """High-level administrative statistics."""

    total_employees: int
    total_departments: int
    total_teams: int
    attendance_today: int
    pending_requests: int


class AdminAttendanceSummaryResponse(BaseModel):
    """Attendance-focused administrative dashboard summary."""

    attendance_today: int
    employees_without_attendance_today: int
    checked_out_today: int
    currently_checked_in: int


class AdminRequestSummaryResponse(BaseModel):
    """Request workflow administrative summary."""

    total_requests: int
    pending_requests: int
    approved_requests: int
    rejected_requests: int
    pending_approval_actions: int


class UserDashboardRequestItem(BaseModel):
    """Compact request item used in the user dashboard."""

    id: int
    request_type_name: str
    status: RequestStatus
    created_at: datetime


class UserDashboardNotification(BaseModel):
    """Derived notification returned by the user dashboard."""

    level: str
    message: str


class UserDashboardSummaryResponse(BaseModel):
    """Personal dashboard summary for authenticated users."""

    employee_id: int
    has_open_attendance: bool
    pending_requests: int
    pending_approvals: int
    recent_requests: list[UserDashboardRequestItem]
    notifications: list[UserDashboardNotification]
