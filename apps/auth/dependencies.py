from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from db.session import get_db
from apps.auth.models import User,UserRole
from apps.auth.services import get_user_by_matricule
from core.security import verify_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Resolve the authenticated user from the bearer token."""
    payload = verify_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    matricule = payload.get("sub")  

    if matricule is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = get_user_by_matricule(db, matricule)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user

def require_active_user(current_user = Depends(get_current_user)):
    """Allow access only to active user accounts."""
    if not current_user.is_active : 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive User account",
        )
    return current_user

def require_superuser(current_user = Depends(require_active_user)):
    """Allow access only to active superusers."""
    if current_user.role != UserRole.SUPERUSER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="you do not have permission to perfom this action "
        )
    return current_user


