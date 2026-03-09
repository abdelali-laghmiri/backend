from sqlalchemy.orm import Session

from apps.auth.models import User
from apps.employees.models import Employee
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
