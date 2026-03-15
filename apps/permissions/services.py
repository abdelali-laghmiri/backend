from sqlalchemy.orm import Session, joinedload

from apps.auth.models import User
from apps.employees.models import Employee
from apps.organization.models import JobTitle
from apps.permissions.models import Permission, JobTitlePermission

# =====================================================
# Permission Services
# Resolves permission checks for authenticated users.
# =====================================================


def user_has_permission(
    db: Session,
    user: User,
    permission_name: str
) -> bool:
    """Check whether the user's job title grants the requested permission."""
    permission = (
        db.query(Permission.id)
        .join(
            JobTitlePermission,
            JobTitlePermission.permission_id == Permission.id,
        )
        .join(
            Employee,
            Employee.job_title_id == JobTitlePermission.job_title_id,
        )
        .filter(
            Employee.user_id == user.id,
            Permission.name == permission_name,
        )
        .first()
    )

    return permission is not None


def list_permissions(db: Session):
    """Return all available permissions ordered by name."""

    return db.query(Permission).order_by(Permission.name).all()


def list_job_title_permissions(db: Session, job_title_id: int):
    """Return all permissions assigned to a job title."""

    job_title = db.query(JobTitle.id).filter(JobTitle.id == job_title_id).first()
    if not job_title:
        raise ValueError("Job title not found")

    return (
        db.query(JobTitlePermission)
        .options(joinedload(JobTitlePermission.permission))
        .filter(JobTitlePermission.job_title_id == job_title_id)
        .order_by(JobTitlePermission.id)
        .all()
    )


def assign_permission_to_job_title(
    db: Session,
    job_title_id: int,
    permission_id: int,
):
    """Assign a permission to a job title once."""

    job_title = db.query(JobTitle.id).filter(JobTitle.id == job_title_id).first()
    if not job_title:
        raise ValueError("Job title not found")

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise ValueError("Permission not found")

    existing_assignment = (
        db.query(JobTitlePermission.id)
        .filter(
            JobTitlePermission.job_title_id == job_title_id,
            JobTitlePermission.permission_id == permission_id,
        )
        .first()
    )
    if existing_assignment:
        raise ValueError("Permission already assigned to this job title")

    assignment = JobTitlePermission(
        job_title_id=job_title_id,
        permission_id=permission_id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return (
        db.query(JobTitlePermission)
        .options(joinedload(JobTitlePermission.permission))
        .filter(JobTitlePermission.id == assignment.id)
        .first()
    )


def remove_permission_from_job_title(
    db: Session,
    job_title_id: int,
    permission_id: int,
):
    """Remove a permission assignment from a job title."""

    assignment = (
        db.query(JobTitlePermission)
        .filter(
            JobTitlePermission.job_title_id == job_title_id,
            JobTitlePermission.permission_id == permission_id,
        )
        .first()
    )
    if not assignment:
        raise ValueError("Permission assignment not found")

    db.delete(assignment)
    db.commit()
    return True
