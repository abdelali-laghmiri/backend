from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends


from db.session import get_db
from apps.auth.schemas import LoginRequest,TokenResponse,UserResponse
from apps.auth.services import authenticate_user
from core.security import create_access_token

from apps.auth.dependencies import get_current_user,require_superuser


router = APIRouter(prefix="/auth",tags=["Auth"])


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Authenticate a user and issue a JWT access token."""
    user = authenticate_user(db, form_data.username, form_data.password)

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
    }

@router.get("/me",response_model=UserResponse)
def get_me(current_user = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user

@router.get("/admin_only")
def admin_only(user = Depends(require_superuser)):
    """Example endpoint protected by the superuser dependency."""
    return{"message":"welcomsuper user"}
