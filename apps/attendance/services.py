from datetime import datetime, timezone

from sqlalchemy.orm import Session

from apps.attendance.models import Attendance
from apps.auth.models import User
from apps.employees.models import Employee, EmploymentStatus
from apps.employees.services import get_employee_by_user_id
from core.pagination import apply_pagination

# =====================================================
# Attendance Services
# Handles employee check-in, check-out, and history reads.
# =====================================================


def _get_active_employee_for_user(db: Session, current_user: User) -> Employee:
    """Return the current user's employee profile and require an active status."""

    employee = get_employee_by_user_id(db, current_user.id)  # type: ignore[arg-type]
    if employee.employment_status != EmploymentStatus.ACTIVE:
        raise ValueError("Only active employees can use attendance actions")
    return employee


def _get_open_attendance(db: Session, employee_id: int) -> Attendance | None:
    """Return the employee's latest open attendance record, if any."""

    return (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee_id,
            Attendance.check_out.is_(None),
        )
        .order_by(Attendance.check_in.desc(), Attendance.id.desc())
        .first()
    )


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""

    return datetime.now(timezone.utc)


def _as_utc(value: datetime) -> datetime:
    """Normalize database datetimes to UTC-aware values for comparisons."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def check_in_employee(db: Session, current_user: User) -> Attendance:
    """Create a new check-in record for the current employee."""

    employee = _get_active_employee_for_user(db, current_user)

    open_attendance = _get_open_attendance(db, employee.id)
    if open_attendance:
        raise ValueError("Employee is already checked in")

    attendance = Attendance(
        employee_id=employee.id,
        check_in=_utcnow(),
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def check_out_employee(db: Session, current_user: User) -> Attendance:
    """Close the current employee's open attendance record."""

    employee = _get_active_employee_for_user(db, current_user)

    attendance = _get_open_attendance(db, employee.id)
    if not attendance:
        raise ValueError("No open attendance record found")

    check_out_time = _utcnow()
    if check_out_time <= _as_utc(attendance.check_in):
        raise ValueError("Check-out time must be after check-in")

    attendance.check_out = check_out_time
    db.commit()
    db.refresh(attendance)
    return attendance


def get_my_attendance(
    db: Session,
    current_user: User,
    limit: int | None = None,
    offset: int = 0,
):
    """Return the full attendance history of the current employee."""

    employee = get_employee_by_user_id(db, current_user.id)  # type: ignore[arg-type]
    query = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee.id)
        .order_by(Attendance.check_in.desc(), Attendance.id.desc())
    )
    return apply_pagination(query, limit, offset).all()


def get_employee_attendance(
    db: Session,
    employee_id: int,
    limit: int | None = None,
    offset: int = 0,
):
    """Return the attendance history of a specific employee."""

    employee_exists = db.query(Employee.id).filter(Employee.id == employee_id).first()
    if not employee_exists:
        raise ValueError("Employee not found")

    query = (
        db.query(Attendance)
        .filter(Attendance.employee_id == employee_id)
        .order_by(Attendance.check_in.desc(), Attendance.id.desc())
    )
    return apply_pagination(query, limit, offset).all()
