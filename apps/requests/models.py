from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from db.base import Base

# =====================================================
# Request Workflow Models
# Stores request definitions, dynamic form fields,
# workflow steps, and approvals.
# =====================================================


# =========================
# ENUMS
# =========================

class RequestStatus(str, enum.Enum):
    """Overall lifecycle state of a request."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalStatus(str, enum.Enum):
    """Status of an individual approval step."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RequestFieldType(str, enum.Enum):
    """Supported field types for dynamic request forms."""

    TEXT = "TEXT"
    TEXTAREA = "TEXTAREA"
    NUMBER = "NUMBER"
    DATE = "DATE"
    DATETIME = "DATETIME"
    SELECT = "SELECT"
    BOOLEAN = "BOOLEAN"
    FILE = "FILE"


# =========================
# REQUEST TYPES
# =========================

class RequestType(Base):
    """Request category that owns a form schema and approval workflow."""

    __tablename__ = "request_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fields = relationship(
        "RequestTypeField",
        back_populates="request_type",
        cascade="all, delete",
    )
    approval_steps = relationship(
        "ApprovalStep",
        back_populates="request_type",
        cascade="all, delete",
    )
    requests = relationship("Request", back_populates="request_type")


# =========================
# REQUEST TYPE FIELDS
# =========================

class RequestTypeField(Base):
    """Dynamic field definition used to build the request form."""

    __tablename__ = "request_type_fields"

    id = Column(Integer, primary_key=True, index=True)
    request_type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)
    name = Column(String, nullable=False)
    label = Column(String, nullable=False)
    field_type = Column(Enum(RequestFieldType), nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    placeholder = Column(String, nullable=True)
    options = Column(JSON, nullable=True)
    field_order = Column(Integer, nullable=False)
    default_value = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    request_type = relationship("RequestType", back_populates="fields")

    __table_args__ = (
        UniqueConstraint("request_type_id", "name", name="uix_request_type_field_name"),
        UniqueConstraint("request_type_id", "field_order", name="uix_request_type_field_order"),
    )


# =========================
# APPROVAL WORKFLOW
# =========================

class ApprovalStep(Base):
    """Single workflow step tied to the job title that must approve it."""

    __tablename__ = "approval_steps"

    id = Column(Integer, primary_key=True, index=True)
    request_type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    job_title_id = Column(Integer, ForeignKey("job_titles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    request_type = relationship(
        "RequestType",
        back_populates="approval_steps",
    )
    job_title = relationship("JobTitle")

    __table_args__ = (
        UniqueConstraint("request_type_id", "step_order", name="uix_request_step_order"),
    )


# =========================
# REQUEST
# =========================

class Request(Base):
    """Employee request instance that moves through the approval workflow."""

    __tablename__ = "requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    request_type_id = Column(Integer, ForeignKey("request_types.id"), nullable=False)
    status = Column(
        Enum(RequestStatus),
        default=RequestStatus.PENDING,
        nullable=False,
    )
    current_step = Column(Integer, nullable=True)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee")
    request_type = relationship("RequestType", back_populates="requests")
    approvals = relationship(
        "RequestApproval",
        back_populates="request",
        cascade="all, delete",
    )


# =========================
# REQUEST APPROVAL HISTORY
# =========================

class RequestApproval(Base):
    """Approval record generated for a specific request workflow step."""

    __tablename__ = "request_approvals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    approver_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(
        Enum(ApprovalStatus),
        default=ApprovalStatus.PENDING,
        nullable=False,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)

    request = relationship(
        "Request",
        back_populates="approvals",
    )
    approver = relationship("User")
