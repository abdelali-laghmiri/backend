from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from apps.auth.models import User
from apps.employees.models import Employee
from apps.employees.services import get_employee_by_user_id
from apps.organization.models import JobTitle, PositionScope
from apps.requests.models import (
    ApprovalStatus,
    ApprovalStep,
    Request,
    RequestApproval,
    RequestFieldType,
    RequestStatus,
    RequestType,
    RequestTypeField,
)

# =====================================================
# Request Services
# Handles request type configuration, dynamic field setup,
# workflow creation, request submission, and approvals.
# =====================================================


# =====================================================
# Request Type Service
# Handles creation and retrieval of request types.
# =====================================================


def get_request_type_or_error(db: Session, request_type_id: int) -> RequestType:
    """Return a request type or raise a clear error when it does not exist."""

    request_type = db.query(RequestType).filter(RequestType.id == request_type_id).first()
    if not request_type:
        raise ValueError("Request type not found")
    return request_type


def create_request_type(
    db: Session,
    name: str,
    description: str | None = None,
) -> RequestType:
    """Create a new request type after validating uniqueness."""

    existing = db.query(RequestType.id).filter(RequestType.name == name).first()
    if existing:
        raise ValueError("Request type already exists")

    request_type = RequestType(
        name=name,
        description=description,
    )

    db.add(request_type)
    db.commit()
    db.refresh(request_type)
    return request_type


def list_request_types(db: Session):
    """Return all request types ordered by their creation identifier."""

    return db.query(RequestType).order_by(RequestType.id).all()


# =====================================================
# Request Type Fields Service
# Handles dynamic form fields configuration.
# =====================================================


def get_request_type_field_or_error(db: Session, field_id: int) -> RequestTypeField:
    """Return a request type field or raise a clear error when it is missing."""

    field = db.query(RequestTypeField).filter(RequestTypeField.id == field_id).first()
    if not field:
        raise ValueError("Request type field not found")
    return field


def validate_request_type_field_config(
    field_type: RequestFieldType,
    options: list[Any] | None,
    field_order: int,
):
    """Validate field configuration before it is persisted."""

    if field_order <= 0:
        raise ValueError("Field order must be greater than 0")

    if field_type == RequestFieldType.SELECT:
        if not options or not isinstance(options, list):
            raise ValueError("SELECT fields must define a non-empty options list")
    elif options is not None and not isinstance(options, list):
        raise ValueError("Field options must be provided as a list")


def create_request_type_field(
    db: Session,
    request_type_id: int,
    name: str,
    label: str,
    field_type: RequestFieldType,
    is_required: bool = False,
    placeholder: str | None = None,
    options: list[Any] | None = None,
    field_order: int = 1,
    default_value: Any | None = None,
    is_active: bool = True,
) -> RequestTypeField:
    """Create a dynamic form field for a request type."""

    get_request_type_or_error(db, request_type_id)
    validate_request_type_field_config(field_type, options, field_order)

    existing_name = (
        db.query(RequestTypeField.id)
        .filter(
            RequestTypeField.request_type_id == request_type_id,
            RequestTypeField.name == name,
        )
        .first()
    )
    if existing_name:
        raise ValueError("A field with this name already exists for the request type")

    existing_order = (
        db.query(RequestTypeField.id)
        .filter(
            RequestTypeField.request_type_id == request_type_id,
            RequestTypeField.field_order == field_order,
        )
        .first()
    )
    if existing_order:
        raise ValueError("A field with this order already exists for the request type")

    field = RequestTypeField(
        request_type_id=request_type_id,
        name=name,
        label=label,
        field_type=field_type,
        is_required=is_required,
        placeholder=placeholder,
        options=options,
        field_order=field_order,
        default_value=default_value,
        is_active=is_active,
    )

    db.add(field)
    db.commit()
    db.refresh(field)
    return field


def list_request_type_fields(db: Session, request_type_id: int):
    """Return all configured fields for a request type ordered by field order."""

    get_request_type_or_error(db, request_type_id)

    return (
        db.query(RequestTypeField)
        .filter(RequestTypeField.request_type_id == request_type_id)
        .order_by(RequestTypeField.field_order, RequestTypeField.id)
        .all()
    )


def update_request_type_field(
    db: Session,
    field_id: int,
    data: dict[str, Any],
) -> RequestTypeField:
    """Apply partial updates to a dynamic request type field."""

    field = get_request_type_field_or_error(db, field_id)

    new_name = data.get("name", field.name)
    new_field_type = data.get("field_type", field.field_type)
    new_options = data.get("options", field.options)
    new_field_order = data.get("field_order", field.field_order)

    validate_request_type_field_config(new_field_type, new_options, new_field_order)

    existing_name = (
        db.query(RequestTypeField.id)
        .filter(
            RequestTypeField.request_type_id == field.request_type_id,
            RequestTypeField.name == new_name,
            RequestTypeField.id != field.id,
        )
        .first()
    )
    if existing_name:
        raise ValueError("A field with this name already exists for the request type")

    existing_order = (
        db.query(RequestTypeField.id)
        .filter(
            RequestTypeField.request_type_id == field.request_type_id,
            RequestTypeField.field_order == new_field_order,
            RequestTypeField.id != field.id,
        )
        .first()
    )
    if existing_order:
        raise ValueError("A field with this order already exists for the request type")

    for key, value in data.items():
        setattr(field, key, value)

    db.commit()
    db.refresh(field)
    return field


def delete_request_type_field(db: Session, field_id: int):
    """Delete a dynamic request type field."""

    field = get_request_type_field_or_error(db, field_id)
    db.delete(field)
    db.commit()
    return True


def get_request_type_form(db: Session, request_type_id: int):
    """Return the active field definitions used to build a request form."""

    request_type = get_request_type_or_error(db, request_type_id)

    fields = (
        db.query(RequestTypeField)
        .filter(
            RequestTypeField.request_type_id == request_type_id,
            RequestTypeField.is_active.is_(True),
        )
        .order_by(RequestTypeField.field_order, RequestTypeField.id)
        .all()
    )

    return {
        "request_type_id": request_type.id,
        "request_type_name": request_type.name,
        "fields": [
            {
                "name": field.name,
                "label": field.label,
                "field_type": field.field_type,
                "is_required": field.is_required,
                "placeholder": field.placeholder,
                "options": field.options,
                "order": field.field_order,
                "default_value": field.default_value,
            }
            for field in fields
        ],
    }


# =====================================================
# Approval Step Service
# Handles workflow step creation and retrieval.
# =====================================================


def create_approval_step(
    db: Session,
    request_type_id: int,
    step_order: int,
    job_title_id: int,
) -> ApprovalStep:
    """Create a workflow step for a request type."""

    get_request_type_or_error(db, request_type_id)

    job_title = db.query(JobTitle.id).filter(JobTitle.id == job_title_id).first()
    if not job_title:
        raise ValueError("Job title not found")

    if step_order <= 0:
        raise ValueError("Step order must be greater than 0")

    existing = (
        db.query(ApprovalStep.id)
        .filter(
            ApprovalStep.request_type_id == request_type_id,
            ApprovalStep.step_order == step_order,
        )
        .first()
    )
    if existing:
        raise ValueError("A workflow step with this order already exists")

    step = ApprovalStep(
        request_type_id=request_type_id,
        step_order=step_order,
        job_title_id=job_title_id,
    )

    db.add(step)
    db.commit()
    db.refresh(step)
    return step


def get_request_type_steps(db: Session, request_type_id: int):
    """Return workflow steps for a request type ordered by step number."""

    get_request_type_or_error(db, request_type_id)

    return (
        db.query(ApprovalStep)
        .filter(ApprovalStep.request_type_id == request_type_id)
        .order_by(ApprovalStep.step_order)
        .all()
    )


# =====================================================
# Request Validation Service
# Validates submitted request data against form fields.
# =====================================================


def normalize_datetime_value(value: str) -> str:
    """Normalize ISO datetime strings so Python can parse UTC values."""

    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value


def get_select_option_values(options: list[Any] | None) -> list[Any]:
    """Extract comparable values from SELECT field options."""

    if not options or not isinstance(options, list):
        raise ValueError("SELECT fields must define a non-empty options list")

    values: list[Any] = []

    for option in options:
        if isinstance(option, dict):
            if "value" in option:
                values.append(option["value"])
            elif "id" in option:
                values.append(option["id"])
            elif "name" in option:
                values.append(option["name"])
            elif "label" in option:
                values.append(option["label"])
            else:
                raise ValueError("SELECT field options must define a value")
        else:
            values.append(option)

    return values


def validate_request_field_value(field: RequestTypeField, value: Any):
    """Validate a single request field value according to its configured type."""

    if value is None:
        return

    if field.field_type in (RequestFieldType.TEXT, RequestFieldType.TEXTAREA):
        if not isinstance(value, str):
            raise ValueError(f"Field '{field.name}' must be a string")
        return

    if field.field_type == RequestFieldType.NUMBER:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"Field '{field.name}' must be a number")
        return

    if field.field_type == RequestFieldType.DATE:
        if not isinstance(value, str):
            raise ValueError(f"Field '{field.name}' must be a valid ISO date string")
        try:
            date.fromisoformat(value)
        except ValueError as exc:
            raise ValueError(f"Field '{field.name}' must be a valid ISO date string") from exc
        return

    if field.field_type == RequestFieldType.DATETIME:
        if not isinstance(value, str):
            raise ValueError(f"Field '{field.name}' must be a valid ISO datetime string")
        try:
            datetime.fromisoformat(normalize_datetime_value(value))
        except ValueError as exc:
            raise ValueError(f"Field '{field.name}' must be a valid ISO datetime string") from exc
        return

    if field.field_type == RequestFieldType.BOOLEAN:
        if not isinstance(value, bool):
            raise ValueError(f"Field '{field.name}' must be a boolean")
        return

    if field.field_type == RequestFieldType.FILE:
        if not isinstance(value, (str, dict)):
            raise ValueError(f"Field '{field.name}' must be a file reference or metadata object")
        return

    if field.field_type == RequestFieldType.SELECT:
        allowed_values = get_select_option_values(field.options)
        if value not in allowed_values:
            raise ValueError(f"Field '{field.name}' must match one of the allowed options")
        return


def validate_request_extra_data(
    db: Session,
    request_type_id: int,
    extra_data: dict[str, Any] | None,
):
    """Validate request data against the active form fields of the request type."""

    get_request_type_or_error(db, request_type_id)

    fields = (
        db.query(RequestTypeField)
        .filter(
            RequestTypeField.request_type_id == request_type_id,
            RequestTypeField.is_active.is_(True),
        )
        .order_by(RequestTypeField.field_order, RequestTypeField.id)
        .all()
    )

    payload = extra_data or {}
    if not isinstance(payload, dict):
        raise ValueError("Request data must be a JSON object")

    field_map = {field.name: field for field in fields}

    unknown_fields = sorted(set(payload.keys()) - set(field_map.keys()))
    if unknown_fields:
        raise ValueError(f"Unknown fields: {', '.join(unknown_fields)}")

    for field in fields:
        if field.is_required:
            value = payload.get(field.name)
            if field.name not in payload or value is None or (isinstance(value, str) and not value.strip()):
                raise ValueError(f"Field '{field.name}' is required")

    for field_name, value in payload.items():
        validate_request_field_value(field_map[field_name], value)


# =====================================================
# Request Workflow Helpers
# Shared helper functions used by request actions.
# =====================================================


def find_approver_by_job_title(
    db: Session,
    employee: Employee,
    job_title: JobTitle,
):
    """Resolve the approver user according to the job title scope."""

    scope = job_title.scope

    query = db.query(Employee).filter(
        Employee.job_title_id == job_title.id
    )

    if scope == PositionScope.TEAM:  # type: ignore
        query = query.filter(
            Employee.team_id == employee.team_id
        )

    elif scope == PositionScope.DEPARTMENT:  # type: ignore
        query = query.filter(
            Employee.department_id == employee.department_id
        )

    approver = query.first()

    if not approver:
        raise ValueError("Approver not found")

    return approver.user_id


def get_pending_approval_for_request(
    db: Session,
    request_id: int,
    current_user: User,
) -> RequestApproval:
    """Return the current pending approval assigned to the current user."""

    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise ValueError("Request not found")

    if request.status != RequestStatus.PENDING or request.current_step is None:  # type: ignore
        raise ValueError("Request is not awaiting approval")

    approval = (
        db.query(RequestApproval)
        .filter(
            RequestApproval.request_id == request.id,
            RequestApproval.step_order == request.current_step,
            RequestApproval.approver_user_id == current_user.id,
            RequestApproval.status == ApprovalStatus.PENDING,
        )
        .first()
    )

    if not approval:
        raise ValueError("Approval not found")

    return approval


# =====================================================
# Request Service
# Handles creation and retrieval of employee requests.
# =====================================================


def create_request(
    db: Session,
    current_user: User,
    request_type_id: int,
    extra_data: dict | None = None,
):
    """Create a request and generate its approval records."""

    employee = get_employee_by_user_id(db, current_user.id)  # type: ignore

    if not employee:
        raise ValueError("Employee profile not found")

    validate_request_extra_data(db, request_type_id, extra_data)

    steps = (
        db.query(ApprovalStep)
        .filter(ApprovalStep.request_type_id == request_type_id)
        .order_by(ApprovalStep.step_order)
        .all()
    )

    if not steps:
        raise ValueError("No approval workflow defined")

    request = Request(
        employee_id=employee.id,
        request_type_id=request_type_id,
        status=RequestStatus.PENDING,
        current_step=1,
        extra_data=extra_data,
    )

    db.add(request)
    db.flush()

    for step in steps:
        # Each workflow step is materialized so the assigned approver is fixed
        # at request creation time.
        approver_user_id = find_approver_by_job_title(
            db,
            employee,
            step.job_title,
        )

        approval = RequestApproval(
            request_id=request.id,
            step_order=step.step_order,
            approver_user_id=approver_user_id,
            status=ApprovalStatus.PENDING,
        )

        db.add(approval)

    db.commit()
    db.refresh(request)
    return request


def get_my_requests(
    db: Session,
    current_user: User,
):
    """Return the requests created by the current user."""

    employee = get_employee_by_user_id(db, current_user.id)  # type: ignore

    return (
        db.query(Request)
        .filter(Request.employee_id == employee.id)
        .order_by(Request.id)
        .all()
    )


def get_my_approvals(
    db: Session,
    current_user: User,
):
    """Return actionable approval tasks assigned to the current user."""

    return (
        db.query(RequestApproval)
        .join(Request, Request.id == RequestApproval.request_id)
        .filter(
            RequestApproval.approver_user_id == current_user.id,
            RequestApproval.status == ApprovalStatus.PENDING,
            Request.status == RequestStatus.PENDING,
            Request.current_step == RequestApproval.step_order,
        )
        .order_by(RequestApproval.request_id, RequestApproval.step_order)
        .all()
    )


# =====================================================
# Approval Action Service
# Handles approve and reject actions on workflow steps.
# =====================================================


def approve_request(
    db: Session,
    request_id: int,
    current_user: User,
    comment: str | None = None,
):
    """Approve the current workflow step and advance the request."""

    # Approval comments are accepted by the API contract, but the current
    # data model does not persist them.
    _ = comment

    approval = get_pending_approval_for_request(db, request_id, current_user)

    approval.status = ApprovalStatus.APPROVED  # type: ignore
    approval.approved_at = datetime.utcnow()  # type: ignore

    request = approval.request

    # Move the request to the next workflow step, or finalize it when the
    # current approval completes the workflow.
    next_step = request.current_step + 1

    next_approval = db.query(RequestApproval).filter(
        RequestApproval.request_id == request.id,
        RequestApproval.step_order == next_step,
    ).first()

    if next_approval:
        request.current_step = next_step
    else:
        request.status = RequestStatus.APPROVED
        request.current_step = None

    db.commit()
    return True


def reject_request(
    db: Session,
    request_id: int,
    current_user: User,
    comment: str | None = None,
):
    """Reject the current workflow step and close the request."""

    # Approval comments are accepted by the API contract, but the current
    # data model does not persist them.
    _ = comment

    approval = get_pending_approval_for_request(db, request_id, current_user)

    approval.status = ApprovalStatus.REJECTED  # type: ignore
    approval.approved_at = datetime.utcnow()  # type: ignore

    request = approval.request
    request.status = RequestStatus.REJECTED
    request.current_step = None

    db.commit()
    return True
