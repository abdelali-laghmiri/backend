from sqlalchemy.orm import Session, joinedload, selectinload

from apps.auth.models import User
from apps.organization.models import Department, JobTitle, Team
from apps.organization.schemas import JobTitleCreate

# =====================================================
# Organization Services
# Business rules for job titles, departments, and teams.
# =====================================================


def create_job_title(db: Session, data: JobTitleCreate) -> JobTitle:
    """Create a job title after validating uniqueness and hierarchy level."""
    existing = db.query(JobTitle.id).filter(JobTitle.title == data.title).first()
    if existing:
        raise ValueError("Job title already exists")
    if data.level <= 0:
        raise ValueError("Level must be greater than 0")

    job_title = JobTitle(
        title=data.title,
        scope=data.scope,
        level=data.level,
        description=data.description,
        monthly_leave_accrual=data.monthly_leave_accrual,
    )
    db.add(job_title)
    db.commit()
    db.refresh(job_title)
    return job_title


def delete_job_title(db: Session, job_title_id: int):
    """Delete a job title by its identifier."""
    job_title = db.query(JobTitle).filter(JobTitle.id == job_title_id).first()
    if not job_title:
        raise ValueError("Job title not found")

    db.delete(job_title)
    db.commit()
    return True


def create_department(db: Session, name: str, description: str | None, manager_id: int | None):
    """Create a department and optionally assign a manager."""
    existing = db.query(Department.id).filter(Department.name == name).first()
    if existing:
        raise ValueError("Department already exists")

    if manager_id:
        manager = db.query(User.id).filter(User.id == manager_id).first()
        if not manager:
            raise ValueError("Manager not found")

    department = Department(
        name=name,
        description=description,
        manager_id=manager_id,
    )

    db.add(department)
    db.commit()
    db.refresh(department)
    return department


def list_departments(db: Session):
    """List departments with manager and team relationships preloaded."""
    return (
        db.query(Department)
        .options(
            joinedload(Department.manager),
            selectinload(Department.teams),
        )
        .order_by(Department.id)
        .all()
    )


def delete_department(db: Session, department_id: int):
    """Delete a department only when it no longer contains teams."""
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise ValueError("Department not found")

    has_teams = db.query(Team.id).filter(Team.department_id == department_id).first()
    if has_teams:
        raise ValueError("Cannot delete department with existing teams")

    db.delete(department)
    db.commit()
    return True


def create_team(
    db: Session,
    name: str,
    department_id: int,
    team_leader_id: int | None,
):
    """Create a team inside a department with an optional leader."""
    department_exists = db.query(Department.id).filter(Department.id == department_id).first()
    if not department_exists:
        raise ValueError("Department not found")

    existing = (
        db.query(Team.id)
        .filter(Team.name == name, Team.department_id == department_id)
        .first()
    )
    if existing:
        raise ValueError("Team already exists in this department")

    if team_leader_id:
        leader = db.query(User.id).filter(User.id == team_leader_id).first()
        if not leader:
            raise ValueError("Team leader not found")

    team = Team(
        name=name,
        department_id=department_id,
        team_leader_id=team_leader_id,
    )

    db.add(team)
    db.commit()
    db.refresh(team)
    return team


def list_teams(db: Session):
    """List teams together with their department and team leader."""
    return (
        db.query(Team)
        .options(
            joinedload(Team.department),
            joinedload(Team.team_leader),
        )
        .order_by(Team.id)
        .all()
    )


def delete_team(db: Session, team_id: int):
    """Delete a team by its identifier."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise ValueError("Team not found")

    db.delete(team)
    db.commit()
    return True


def get_teams_by_department(db: Session, department_id: int):
    """Return the teams that belong to the specified department."""
    department_exists = db.query(Department.id).filter(Department.id == department_id).first()
    if not department_exists:
        raise ValueError("Department not found")

    return (
        db.query(Team)
        .options(
            joinedload(Team.department),
            joinedload(Team.team_leader),
        )
        .filter(Team.department_id == department_id)
        .order_by(Team.id)
        .all()
    )
