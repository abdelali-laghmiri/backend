from pydantic import BaseModel, ConfigDict
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

class UserResponse(BaseModel):
    """Public representation of the authenticated user."""

    id: int
    matricule: str
    role: UserRole
    is_active: bool
    created_at: datetime
    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)
