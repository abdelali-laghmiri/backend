from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict

from apps.requests.models import RequestFieldType

# =====================================================
# Request Schemas
# Pydantic models for request types, dynamic form fields,
# workflow steps, employee requests, and approval actions.
# =====================================================


class RequestStatus(str, Enum):
    """Serialized status of a request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalStatus(str, Enum):
    """Serialized status of an approval step."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


# =====================================================
# Request Type Schemas
# Defines payloads for request type configuration.
# =====================================================


class RequestTypeBase(BaseModel):
    """Shared fields used by request type payloads."""

    name: str
    description: str | None = None


class RequestTypeCreate(RequestTypeBase):
    """Payload used to create a new request type."""

    pass


class RequestTypeResponse(RequestTypeBase):
    """Serialized representation of a request type."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================
# Request Type Field Schemas
# Defines payloads for dynamic form field configuration.
# =====================================================


class RequestTypeFieldBase(BaseModel):
    """Shared fields used by request type field payloads."""

    name: str
    label: str
    field_type: RequestFieldType
    is_required: bool = False
    placeholder: str | None = None
    options: list[Any] | None = None
    field_order: int
    default_value: Any | None = None
    is_active: bool = True


class RequestTypeFieldCreate(RequestTypeFieldBase):
    """Payload used to create a dynamic field for a request type."""

    pass


class RequestTypeFieldUpdate(BaseModel):
    """Payload used to partially update a request type field."""

    name: str | None = None
    label: str | None = None
    field_type: RequestFieldType | None = None
    is_required: bool | None = None
    placeholder: str | None = None
    options: list[Any] | None = None
    field_order: int | None = None
    default_value: Any | None = None
    is_active: bool | None = None


class RequestTypeFieldResponse(RequestTypeFieldBase):
    """Serialized representation of a request type field."""

    id: int
    request_type_id: int

    model_config = ConfigDict(from_attributes=True)


# =====================================================
# Form Schema Schemas
# Defines payloads used by the frontend to build forms.
# =====================================================


class RequestTypeFormFieldResponse(BaseModel):
    """Serialized field definition returned by the form schema endpoint."""

    name: str
    label: str
    field_type: RequestFieldType
    is_required: bool
    placeholder: str | None = None
    options: list[Any] | None = None
    order: int
    default_value: Any | None = None


class RequestTypeFormResponse(BaseModel):
    """Serialized form schema for a request type."""

    request_type_id: int
    request_type_name: str
    fields: list[RequestTypeFormFieldResponse]


# =====================================================
# Approval Step Schemas
# Defines payloads for workflow step configuration.
# =====================================================


class ApprovalStepBase(BaseModel):
    """Shared fields used by approval step payloads."""

    request_type_id: int
    step_order: int
    job_title_id: int


class ApprovalStepCreate(ApprovalStepBase):
    """Payload used to create a workflow approval step."""

    pass


class ApprovalStepResponse(ApprovalStepBase):
    """Serialized representation of a workflow approval step."""

    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================
# Request Schemas
# Defines payloads for employee request creation and reads.
# =====================================================


class RequestCreate(BaseModel):
    """Payload used when an employee creates a request."""

    request_type_id: int
    extra_data: dict[str, Any] | None = None


class RequestResponse(BaseModel):
    """Serialized representation of a request."""

    id: int
    employee_id: int
    request_type_id: int
    status: RequestStatus
    current_step: int | None
    extra_data: dict[str, Any] | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =====================================================
# Approval Schemas
# Defines payloads for approval inbox responses and actions.
# =====================================================


class ApprovalResponse(BaseModel):
    """Serialized representation of a generated approval step."""

    id: int
    request_id: int
    approver_user_id: int
    step_order: int
    status: ApprovalStatus
    approved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ApprovalAction(BaseModel):
    """Optional payload sent when approving or rejecting a request."""

    comment: str | None = None


class ActionResponse(BaseModel):
    """Simple response payload returned by workflow actions."""

    message: str
