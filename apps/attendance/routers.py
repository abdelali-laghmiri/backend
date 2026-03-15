from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.attendance.schemas import AttendanceResponse
from apps.attendance.services import (
    check_in_employee,
    check_out_employee,
    get_employee_attendance,
    get_my_attendance,
)
from apps.auth.dependencies import require_active_user
from apps.auth.models import User
from apps.permissions.dependencies import require_permission
from core.pagination import limit_query, offset_query
from db.session import get_db

router = APIRouter(prefix="/attendance", tags=["Attendance"])

# =====================================================
# Attendance Router
# Exposes attendance punch and history endpoints.
# =====================================================


@router.post("/check-in", response_model=AttendanceResponse)
def check_in_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Create a new attendance check-in for the authenticated employee."""

    try:
        return check_in_employee(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/check-out", response_model=AttendanceResponse)
def check_out_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Check out the authenticated employee from the current attendance record."""

    try:
        return check_out_employee(db, current_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=list[AttendanceResponse])
def my_attendance_endpoint(
    limit: int | None = Depends(limit_query),
    offset: int = Depends(offset_query),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Return the authenticated employee's attendance history."""

    try:
        return get_my_attendance(db, current_user, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/employee/{employee_id}", response_model=list[AttendanceResponse])
def employee_attendance_endpoint(
    employee_id: int,
    limit: int | None = Depends(limit_query),
    offset: int = Depends(offset_query),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("attendance.read_employee")),
):
    """Return attendance history for a specific employee."""

    try:
        return get_employee_attendance(db, employee_id, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
