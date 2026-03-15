from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from apps.auth.models import UserRole

# =====================================================
# Authentication Schemas
# Defines request and response payloads for auth endpoints.
# =====================================================

class TokenResponse(BaseModel):
    """JWT token returned after a successful authentication."""

    access_token: str
    token_type: str = "bearer"
    requires_password_change: bool = False
    message: str | None = None

class UserResponse(BaseModel):
    """Public representation of the authenticated user."""

    id: int
    matricule: str
    role: UserRole
    is_active: bool
    first_login: bool
    created_at: datetime
    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(BaseModel):
    """Payload used to change the authenticated user's password."""

    old_password: str
    new_password: str = Field(min_length=12, max_length=128)


class AuthActionResponse(BaseModel):
    """Simple response returned by authentication mutation endpoints."""

    message: str
