from pydantic import BaseModel, ConfigDict, Field

# =====================================================
# Permission Schemas
# Pydantic models for permission listing and assignments.
# =====================================================


class PermissionResponse(BaseModel):
    """Serialized permission returned by the permissions API."""

    id: int
    name: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PermissionCreate(BaseModel):
    """Payload used to create a new permission."""

    name: str = Field(min_length=3, max_length=100, pattern=r"^[a-z][a-z0-9_.-]*$")
    description: str | None = Field(default=None, max_length=255)


class JobTitlePermissionAssign(BaseModel):
    """Payload used to assign a permission to a job title."""

    permission_id: int


class JobTitlePermissionResponse(BaseModel):
    """Serialized job title permission assignment."""

    id: int
    job_title_id: int
    permission_id: int
    permission: PermissionResponse

    model_config = ConfigDict(from_attributes=True)


class PermissionActionResponse(BaseModel):
    """Simple response returned by assignment mutation endpoints."""

    message: str
