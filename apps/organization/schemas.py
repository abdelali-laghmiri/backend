from pydantic import BaseModel, ConfigDict
from datetime import datetime

from apps.organization.models import PositionScope

# =====================================================
# Organization Schemas
# Pydantic models for job titles, departments, and teams.
# =====================================================


class JobTitleBase(BaseModel):
    """Shared fields used by job title payloads."""

    title: str
    scope: PositionScope
    level: int
    description: str | None = None
    monthly_leave_accrual: float = 0.0


class JobTitleCreate(JobTitleBase):
    """Payload used to create a new job title."""

    pass


class JobTitleResponse(JobTitleBase):
    """Serialized representation of a job title."""

    id: int
    created_at: datetime

    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)


class DepartmentBase(BaseModel):
    """Shared fields used by department payloads."""

    name: str
    description: str | None = None
    manager_id: int | None = None


class DepartmentCreate(DepartmentBase):
    """Payload used to create a new department."""

    pass


class DepartmentResponse(DepartmentBase):
    """Serialized representation of a department."""

    id: int
    created_at: datetime

    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)


class TeamBase(BaseModel):
    """Shared fields used by team payloads."""

    name: str
    department_id: int
    team_leader_id: int | None = None


class TeamCreate(TeamBase):
    """Payload used to create a new team."""

    pass


class TeamResponse(TeamBase):
    """Serialized representation of a team."""

    id: int

    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)
