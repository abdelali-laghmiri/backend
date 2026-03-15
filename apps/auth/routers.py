from fastapi import Depends
from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from apps.auth.dependencies import get_current_user, require_active_user
from apps.auth.schemas import (
    AuthActionResponse,
    ChangePasswordRequest,
    TokenResponse,
    UserResponse,
)
from apps.auth.services import authenticate_user, change_password
from apps.permissions.services import list_user_permission_names
from core.security import create_access_token
from db.session import get_db


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate a user and issue a JWT access token."""
    try:
        user = authenticate_user(db, form_data.username, form_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={"sub": user.matricule}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "requires_password_change": user.first_login,
        "message": (
            "Password change required before normal use."
            if user.first_login
            else None
        ),
    }


@router.post("/change-password", response_model=AuthActionResponse)
def change_password_endpoint(
    data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_active_user),
):
    """Change the authenticated user's password and clear the first-login flag."""

    try:
        change_password(
            db,
            current_user,
            old_password=data.old_password,
            new_password=data.new_password,
        )
        return {"message": "Password changed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/me", response_model=UserResponse)
def get_me(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Return the currently authenticated user."""
    response = UserResponse.model_validate(current_user, from_attributes=True).model_dump()
    response["permissions"] = list_user_permission_names(db, current_user)
    return response
