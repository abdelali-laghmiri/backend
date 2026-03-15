from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from apps.attendance.models import Attendance
from apps.auth.models import User
from apps.employees.models import Employee
from apps.employees.services import get_employee_by_user_id
from apps.organization.models import Department, Team
from apps.requests.models import ApprovalStatus, Request, RequestApproval, RequestStatus

# =====================================================
# Dashboard Services
# Aggregates application data for admin and user dashboards.
# =====================================================


def _today_utc_date():
    """Return the current UTC date used for daily dashboard statistics."""

    return datetime.now(timezone.utc).date()


def get_admin_dashboard_stats(db: Session):
    """Return high-level counts used by the admin dashboard."""

    today = _today_utc_date()

    return {
        "total_employees": db.query(func.count()).select_from(Employee).scalar() or 0,
        "total_departments": db.query(func.count()).select_from(Department).scalar() or 0,
        "total_teams": db.query(func.count()).select_from(Team).scalar() or 0,
        "attendance_today": (
            db.query(func.count(func.distinct(Attendance.employee_id)))
            .filter(func.date(Attendance.check_in) == today)
            .scalar()
            or 0
        ),
        "pending_requests": (
            db.query(func.count())
            .select_from(Request)
            .filter(Request.status == RequestStatus.PENDING)
            .scalar()
            or 0
        ),
    }


def get_admin_attendance_summary(db: Session):
    """Return attendance-focused statistics for the admin dashboard."""

    today = _today_utc_date()
    total_employees = db.query(func.count()).select_from(Employee).scalar() or 0
    attendance_today = (
        db.query(func.count(func.distinct(Attendance.employee_id)))
        .filter(func.date(Attendance.check_in) == today)
        .scalar()
        or 0
    )
    checked_out_today = (
        db.query(func.count())
        .select_from(Attendance)
        .filter(Attendance.check_out.is_not(None), func.date(Attendance.check_out) == today)
        .scalar()
        or 0
    )
    currently_checked_in = (
        db.query(func.count())
        .select_from(Attendance)
        .filter(Attendance.check_out.is_(None))
        .scalar()
        or 0
    )

    return {
        "attendance_today": attendance_today,
        "employees_without_attendance_today": max(total_employees - attendance_today, 0),
        "checked_out_today": checked_out_today,
        "currently_checked_in": currently_checked_in,
    }


def get_admin_request_summary(db: Session):
    """Return request workflow statistics for administrators."""

    return {
        "total_requests": db.query(func.count()).select_from(Request).scalar() or 0,
        "pending_requests": (
            db.query(func.count())
            .select_from(Request)
            .filter(Request.status == RequestStatus.PENDING)
            .scalar()
            or 0
        ),
        "approved_requests": (
            db.query(func.count())
            .select_from(Request)
            .filter(Request.status == RequestStatus.APPROVED)
            .scalar()
            or 0
        ),
        "rejected_requests": (
            db.query(func.count())
            .select_from(Request)
            .filter(Request.status == RequestStatus.REJECTED)
            .scalar()
            or 0
        ),
        "pending_approval_actions": (
            db.query(func.count())
            .select_from(RequestApproval)
            .join(Request, Request.id == RequestApproval.request_id)
            .filter(
                RequestApproval.status == ApprovalStatus.PENDING,
                Request.status == RequestStatus.PENDING,
                Request.current_step == RequestApproval.step_order,
            )
            .scalar()
            or 0
        ),
    }


def get_user_dashboard_summary(db: Session, current_user: User):
    """Return a personal dashboard summary for the authenticated user."""

    employee = get_employee_by_user_id(db, current_user.id)  # type: ignore[arg-type]

    open_attendance = (
        db.query(Attendance)
        .filter(
            Attendance.employee_id == employee.id,
            Attendance.check_out.is_(None),
        )
        .first()
    )

    recent_requests = (
        db.query(Request)
        .options(joinedload(Request.request_type))
        .filter(Request.employee_id == employee.id)
        .order_by(Request.created_at.desc(), Request.id.desc())
        .limit(5)
        .all()
    )

    pending_requests = (
        db.query(func.count())
        .select_from(Request)
        .filter(
            Request.employee_id == employee.id,
            Request.status == RequestStatus.PENDING,
        )
        .scalar()
        or 0
    )

    pending_approvals = (
        db.query(func.count())
        .select_from(RequestApproval)
        .join(Request, Request.id == RequestApproval.request_id)
        .filter(
            RequestApproval.approver_user_id == current_user.id,
            RequestApproval.status == ApprovalStatus.PENDING,
            Request.status == RequestStatus.PENDING,
            Request.current_step == RequestApproval.step_order,
        )
        .scalar()
        or 0
    )

    notifications: list[dict[str, str]] = []
    if current_user.first_login:
        notifications.append(
            {
                "level": "warning",
                "message": "You must change your temporary password before normal use.",
            }
        )
    if open_attendance:
        notifications.append(
            {
                "level": "info",
                "message": "You are currently checked in and still need to check out.",
            }
        )
    if pending_requests:
        notifications.append(
            {
                "level": "info",
                "message": f"You have {pending_requests} pending request(s).",
            }
        )
    if pending_approvals:
        notifications.append(
            {
                "level": "info",
                "message": f"You have {pending_approvals} approval task(s) waiting.",
            }
        )

    return {
        "employee_id": employee.id,
        "has_open_attendance": open_attendance is not None,
        "pending_requests": pending_requests,
        "pending_approvals": pending_approvals,
        "recent_requests": [
            {
                "id": request.id,
                "request_type_name": request.request_type.name,  # type: ignore[union-attr]
                "status": request.status,
                "created_at": request.created_at,
            }
            for request in recent_requests
        ],
        "notifications": notifications,
    }
