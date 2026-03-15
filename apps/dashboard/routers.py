from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.auth.dependencies import require_active_user
from apps.auth.models import User
from apps.dashboard.schemas import (
    AdminAttendanceSummaryResponse,
    AdminDashboardStatsResponse,
    AdminRequestSummaryResponse,
    UserDashboardSummaryResponse,
)
from apps.dashboard.services import (
    get_admin_attendance_summary,
    get_admin_dashboard_stats,
    get_admin_request_summary,
    get_user_dashboard_summary,
)
from apps.permissions.dependencies import require_permission
from db.session import get_db

# =====================================================
# Dashboard Router
# Exposes admin and personal dashboard aggregation endpoints.
# =====================================================

router = APIRouter(tags=["Dashboard"])


@router.get("/admin/dashboard/stats", response_model=AdminDashboardStatsResponse)
def admin_dashboard_stats_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard.admin.read")),
):
    """Return high-level administrative dashboard statistics."""

    return get_admin_dashboard_stats(db)


@router.get(
    "/admin/dashboard/attendance-summary",
    response_model=AdminAttendanceSummaryResponse,
)
def admin_attendance_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard.admin.read")),
):
    """Return attendance summary metrics for administrators."""

    return get_admin_attendance_summary(db)


@router.get(
    "/admin/dashboard/request-summary",
    response_model=AdminRequestSummaryResponse,
)
def admin_request_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("dashboard.admin.read")),
):
    """Return request workflow summary metrics for administrators."""

    return get_admin_request_summary(db)


@router.get("/dashboard/me/summary", response_model=UserDashboardSummaryResponse)
def user_dashboard_summary_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Return the authenticated user's personal dashboard summary."""

    try:
        return get_user_dashboard_summary(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
