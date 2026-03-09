from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import date

from apps.employees.models import EmploymentStatus

# =====================================================
# Employee Schemas
# Pydantic models for employee creation, updates, and responses.
# =====================================================


class EmployeeCreate(BaseModel):
    """Payload used to create a new employee profile."""

    matricule: str
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    hire_date: date
    department_id: int
    team_id: int
    job_title_id: int


class EmployeeResponse(BaseModel):
    """Detailed employee payload returned by employee endpoints."""

    id: int
    user_id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None
    hire_date: date
    department_id: int
    team_id: int
    job_title_id: int
    current_leave_balance: int
    employment_status: EmploymentStatus

    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)


class EmployeeListResponse(BaseModel):
    """Compact employee payload used for list responses."""

    id: int
    first_name: str
    last_name: str
    department_id: int
    team_id: int
    job_title_id: int
    employment_status: EmploymentStatus

    # Use Pydantic v2 ORM serialization config.
    model_config = ConfigDict(from_attributes=True)


class EmployeeUpdate(BaseModel):
    """Partial payload used to update an employee profile."""

    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    hire_date: date | None = None
    department_id: int | None = None
    team_id: int | None = None
    job_title_id: int | None = None
    employment_status: EmploymentStatus | None = None
