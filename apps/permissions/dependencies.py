from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db

from apps.auth.dependencies import require_active_user
from apps.auth.models import User, UserRole

from apps.permissions.services import user_has_permission


def require_permission(permission_name: str):
    """Build a dependency that checks whether the current user has a permission."""

    def checker(
        db: Session = Depends(get_db),
        current_user: User = Depends(require_active_user)
    ):
        """Validate access for the requested permission name."""

        if current_user.role == UserRole.SUPERUSER:  # type: ignore
            return current_user

        allowed = user_has_permission(
            db,
            current_user,
            permission_name
        )

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )

        return current_user

    return checker
