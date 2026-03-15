from pydantic import BaseModel, ConfigDict

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
