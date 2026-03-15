from dataclasses import dataclass

from sqlalchemy.orm import Session, joinedload

from apps.auth.models import User, UserRole
from apps.auth.services import (
    generate_temporary_password,
    get_password_hash,
    validate_password_strength,
)
from apps.attendance.models import Attendance
from apps.employees.models import Employee
from apps.employees.schemas import EmployeeCreate, EmployeeUpdate
from apps.organization.models import Department, JobTitle, PositionScope, Team
from apps.requests.models import Request, RequestApproval

# =====================================================
# Employee Services
# Handles employee creation, visibility, updates, and deletion.
# =====================================================

# Relationship options reused when employee details need related entities.
EMPLOYEE_LOAD_OPTIONS = (
    joinedload(Employee.job_title),
    joinedload(Employee.department),
    joinedload(Employee.team),
    joinedload(Employee.user),
)


@dataclass
class EmployeeCreateResult:
    """Result returned when an employee is created."""

    employee: Employee
    temporary_password: str | None = None


def _validate_employee_assignment(
    db: Session,
    *,
    department_id: int,
    team_id: int,
    job_title_id: int,
) -> None:
    """Validate organization references for an employee."""

    department_exists = db.query(Department.id).filter(Department.id == department_id).first()
    if not department_exists:
        raise ValueError("Department not found")

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise ValueError("Team not found")

    if team.department_id != department_id:  # type: ignore
        raise ValueError("Team does not belong to the given department")

    job_title_exists = db.query(JobTitle.id).filter(JobTitle.id == job_title_id).first()
    if not job_title_exists:
        raise ValueError("Job title not found")


def create_employee(db: Session, data: EmployeeCreate):
    """Create a user account and its linked employee profile."""
    existing_user = db.query(User.id).filter(User.matricule == data.matricule).first()
    if existing_user:
        raise ValueError("User with this matricule already exists")

    existing_email = db.query(Employee.id).filter(Employee.email == data.email).first()
    if existing_email:
        raise ValueError("Employee with this email already exists")

    _validate_employee_assignment(
        db,
        department_id=data.department_id,
        team_id=data.team_id,
        job_title_id=data.job_title_id,
    )

    temporary_password: str | None = None
    raw_password = data.initial_password
    if not raw_password:
        temporary_password = generate_temporary_password()
        raw_password = temporary_password
    else:
        validate_password_strength(raw_password)

    hashed_password = get_password_hash(raw_password)

    user = User(
        matricule=data.matricule,
        hashed_password=hashed_password,
        role=UserRole.USER,
        is_active=True,
        first_login=True,
    )

    try:
        db.add(user)
        db.flush()

        employee = Employee(
            user_id=user.id,
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            phone=data.phone,
            hire_date=data.hire_date,
            department_id=data.department_id,
            team_id=data.team_id,
            job_title_id=data.job_title_id,
            current_leave_balance=0,
        )

        db.add(employee)
        db.commit()
        db.refresh(employee)
    except Exception:
        db.rollback()
        raise

    created_employee = (
        db.query(Employee)
        .options(*EMPLOYEE_LOAD_OPTIONS)
        .filter(Employee.id == employee.id)
        .first()
    )
    return EmployeeCreateResult(
        employee=created_employee,
        temporary_password=temporary_password,
    )


def get_visible_employees(db: Session, current_user: User):
    """Build the employee query constrained by the current user's scope."""
    if current_user.role == UserRole.SUPERUSER:  # type: ignore
        return db.query(Employee).options(*EMPLOYEE_LOAD_OPTIONS)

    current_employee = get_employee_by_user_id(db, current_user.id)  # type: ignore

    job_title = current_employee.job_title
    scope = job_title.scope
    level = job_title.level

    query = db.query(Employee).options(*EMPLOYEE_LOAD_OPTIONS).join(JobTitle)
    query = query.filter(JobTitle.level < level)

    if scope == PositionScope.GLOBAL:
        return query

    if scope == PositionScope.DEPARTMENT:
        query = query.filter(Employee.department_id == current_employee.department_id)

    if scope == PositionScope.TEAM:
        query = query.filter(Employee.team_id == current_employee.team_id)

    if scope == PositionScope.NONE:
        query = query.filter(Employee.id == current_employee.id)

    return query


def list_employees(
    db: Session,
    current_user: User,
    department_id: int | None = None,
    team_id: int | None = None,
):
    """List employees visible to the current user with optional filters."""
    query = get_visible_employees(db, current_user)

    if department_id:
        query = query.filter(Employee.department_id == department_id)  # type: ignore

    if team_id:
        query = query.filter(Employee.team_id == team_id)  # type: ignore

    return query.order_by(Employee.id).all()  # type: ignore


def get_employee_by_id(db: Session, employee_id: int, current_user: User):
    """Return a single employee if it is visible to the current user."""
    employee = (
        get_visible_employees(db, current_user)
        .filter(Employee.id == employee_id)
        .first()
    )
    if not employee:
        raise ValueError("Employee not found ")

    return employee


def get_employee_by_user_id(db: Session, user_id: int):
    """Return the employee profile linked to a specific user account."""
    employee = (
        db.query(Employee)
        .options(*EMPLOYEE_LOAD_OPTIONS)
        .filter(Employee.user_id == user_id)
        .first()
    )
    if not employee:
        raise ValueError("Employee profile not found")
    return employee


def update_employee(
    db: Session,
    employee_id: int,
    data: EmployeeUpdate,
):
    """Apply partial updates to an employee profile."""
    employee = (
        db.query(Employee)
        .options(*EMPLOYEE_LOAD_OPTIONS)
        .filter(Employee.id == employee_id)
        .first()
    )
    if not employee:
        raise ValueError("Employee not found")

    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_email = (
            db.query(Employee.id)
            .filter(
                Employee.email == update_data["email"],
                Employee.id != employee_id,
            )
            .first()
        )
        if existing_email:
            raise ValueError("Employee with this email already exists")

    department_id = update_data.get("department_id", employee.department_id)
    team_id = update_data.get("team_id", employee.team_id)
    job_title_id = update_data.get("job_title_id", employee.job_title_id)
    _validate_employee_assignment(
        db,
        department_id=department_id,
        team_id=team_id,
        job_title_id=job_title_id,
    )

    for key, value in update_data.items():
        setattr(employee, key, value)

    try:
        db.commit()
        db.refresh(employee)
    except Exception:
        db.rollback()
        raise

    return (
        db.query(Employee)
        .options(*EMPLOYEE_LOAD_OPTIONS)
        .filter(Employee.id == employee.id)
        .first()
    )


def delete_employee(db: Session, employee_id: int):
    """Delete an employee profile and its linked user account."""
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")

    user = db.query(User).filter(User.id == employee.user_id).first()

    has_requests = db.query(Request.id).filter(Request.employee_id == employee.id).first()
    if has_requests:
        raise ValueError("Cannot delete employee with existing requests")

    has_attendance = (
        db.query(Attendance.id)
        .filter(Attendance.employee_id == employee.id)
        .first()
    )
    if has_attendance:
        raise ValueError("Cannot delete employee with attendance history")

    has_pending_approvals = (
        db.query(RequestApproval.id)
        .filter(RequestApproval.approver_user_id == employee.user_id)
        .first()
    )
    if has_pending_approvals:
        raise ValueError("Cannot delete employee with approval history")

    db.query(Department).filter(Department.manager_id == employee.user_id).update(
        {"manager_id": None},
        synchronize_session=False,
    )
    db.query(Team).filter(Team.team_leader_id == employee.user_id).update(
        {"team_leader_id": None},
        synchronize_session=False,
    )

    try:
        db.delete(employee)
        if user:
            db.delete(user)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return True
