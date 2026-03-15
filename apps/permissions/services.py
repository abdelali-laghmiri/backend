from sqlalchemy.orm import Session, joinedload

from apps.auth.models import User
from apps.employees.models import Employee
from apps.organization.models import JobTitle
from apps.permissions.models import Permission, JobTitlePermission
from core.pagination import apply_pagination

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


def list_permissions(
    db: Session,
    limit: int | None = None,
    offset: int = 0,
):
    """Return all available permissions ordered by name."""

    query = db.query(Permission).order_by(Permission.name)
    return apply_pagination(query, limit, offset).all()


def create_permission(
    db: Session,
    name: str,
    description: str | None = None,
) -> Permission:
    """Create a new permission after validating uniqueness."""

    existing = db.query(Permission.id).filter(Permission.name == name).first()
    if existing:
        raise ValueError("Permission already exists")

    permission = Permission(name=name, description=description)
    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


def delete_permission(db: Session, permission_id: int):
    """Delete a permission when it is not assigned to any job title."""

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise ValueError("Permission not found")

    assigned = (
        db.query(JobTitlePermission.id)
        .filter(JobTitlePermission.permission_id == permission_id)
        .first()
    )
    if assigned:
        raise ValueError("Cannot delete a permission that is assigned to a job title")

    db.delete(permission)
    db.commit()
    return True


def list_job_title_permissions(
    db: Session,
    job_title_id: int,
    limit: int | None = None,
    offset: int = 0,
):
    """Return all permissions assigned to a job title."""

    job_title = db.query(JobTitle.id).filter(JobTitle.id == job_title_id).first()
    if not job_title:
        raise ValueError("Job title not found")

    query = (
        db.query(JobTitlePermission)
        .options(joinedload(JobTitlePermission.permission))
        .filter(JobTitlePermission.job_title_id == job_title_id)
        .order_by(JobTitlePermission.id)
    )
    return apply_pagination(query, limit, offset).all()


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
