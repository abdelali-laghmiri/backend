from pydantic import BaseModel, ConfigDict
from datetime import datetime

# =====================================================
# Authentication Schemas
# Defines request and response payloads for auth endpoints.
# =====================================================

class LoginRequest(BaseModel):
    """Credentials payload for a login attempt."""

    matricule: str
    password: str

class TokenResponse(BaseModel):
    """JWT token returned after a successful authentication."""

    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """Public representation of the authenticated user."""

    id: int
    matricule: str
    role : str
    is_active: bool
    created_at: datetime
    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)
