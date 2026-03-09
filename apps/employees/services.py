from sqlalchemy.orm import Session, joinedload

from apps.auth.models import User, UserRole
from apps.auth.services import get_password_hash
from apps.employees.models import Employee
from apps.employees.schemas import EmployeeCreate, EmployeeUpdate
from apps.organization.models import Department, JobTitle, PositionScope, Team

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


def create_employee(db: Session, data: EmployeeCreate):
    """Create a user account and its linked employee profile."""
    existing_user = db.query(User.id).filter(User.matricule == data.matricule).first()
    if existing_user:
        raise ValueError("User with this matricule already exists")

    existing_email = db.query(Employee.id).filter(Employee.email == data.email).first()
    if existing_email:
        raise ValueError("Employee with this email already exists")

    department_exists = db.query(Department.id).filter(Department.id == data.department_id).first()
    if not department_exists:
        raise ValueError("Department not found")

    team = db.query(Team).filter(Team.id == data.team_id).first()
    if not team:
        raise ValueError("Team not found")

    if team.department_id != data.department_id:  # type: ignore
        raise ValueError("Team does not belong to the given department")

    job_title_exists = db.query(JobTitle.id).filter(JobTitle.id == data.job_title_id).first()
    if not job_title_exists:
        raise ValueError("Job title not found")

    default_password = (data.first_name + data.last_name).lower() + "123"
    hashed_password = get_password_hash(default_password)

    user = User(
        matricule=data.matricule,
        hashed_password=hashed_password,
        role=UserRole.USER,
        is_active=True,
        first_login=True,
    )

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

    return (
        db.query(Employee)
        .options(*EMPLOYEE_LOAD_OPTIONS)
        .filter(Employee.id == employee.id)
        .first()
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
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError("Employee not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

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

    db.delete(employee)
    if user:
        db.delete(user)

    db.commit()
    return True
