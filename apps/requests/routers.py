from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.auth.dependencies import get_current_user, require_active_user, require_superuser
from apps.auth.models import User
from db.session import get_db

from . import schemas
from . import services

# =====================================================
# Request Router
# Exposes endpoints for request types, dynamic fields,
# form schemas, workflow steps, requests, and approvals.
# =====================================================


router = APIRouter(
    prefix="/requests",
    tags=["Requests"],
)


# =====================================================
# Request Type Routes
# Handles request type configuration.
# =====================================================


@router.post("/types", response_model=schemas.RequestTypeResponse)
def create_request_type_endpoint(
    data: schemas.RequestTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Create a request type. Restricted to superusers."""

    try:
        return services.create_request_type(
            db,
            name=data.name,
            description=data.description,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/types", response_model=list[schemas.RequestTypeResponse])
def list_request_types_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """List all available request types."""

    return services.list_request_types(db)


# =====================================================
# Request Type Field Routes
# Handles dynamic form fields configuration.
# =====================================================


@router.post("/types/{type_id}/fields", response_model=schemas.RequestTypeFieldResponse)
def create_request_type_field_endpoint(
    type_id: int,
    data: schemas.RequestTypeFieldCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Create a dynamic field for a request type. Restricted to superusers."""

    try:
        return services.create_request_type_field(
            db,
            request_type_id=type_id,
            name=data.name,
            label=data.label,
            field_type=data.field_type,
            is_required=data.is_required,
            placeholder=data.placeholder,
            options=data.options,
            field_order=data.field_order,
            default_value=data.default_value,
            is_active=data.is_active,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/types/{type_id}/fields", response_model=list[schemas.RequestTypeFieldResponse])
def list_request_type_fields_endpoint(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Return configured fields for a request type ordered by field order."""

    try:
        return services.list_request_type_fields(db, type_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.put("/fields/{field_id}", response_model=schemas.RequestTypeFieldResponse)
def update_request_type_field_endpoint(
    field_id: int,
    data: schemas.RequestTypeFieldUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Update a dynamic request type field. Restricted to superusers."""

    try:
        return services.update_request_type_field(
            db,
            field_id,
            data.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete("/fields/{field_id}", response_model=schemas.ActionResponse)
def delete_request_type_field_endpoint(
    field_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Delete a dynamic request type field. Restricted to superusers."""

    try:
        services.delete_request_type_field(db, field_id)
        return {"message": "Request type field deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# Form Schema Routes
# Returns the frontend-ready form schema for request types.
# =====================================================


@router.get("/types/{type_id}/form", response_model=schemas.RequestTypeFormResponse)
def get_request_type_form_endpoint(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Return the active form schema for the given request type."""

    try:
        return services.get_request_type_form(db, type_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# Workflow Step Routes
# Handles approval workflow step configuration.
# =====================================================


@router.post("/steps", response_model=schemas.ApprovalStepResponse)
def create_approval_step_endpoint(
    data: schemas.ApprovalStepCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superuser),
):
    """Create a workflow step for a request type. Restricted to superusers."""

    try:
        return services.create_approval_step(
            db,
            request_type_id=data.request_type_id,
            step_order=data.step_order,
            job_title_id=data.job_title_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/types/{type_id}/steps", response_model=list[schemas.ApprovalStepResponse])
def get_request_type_steps_endpoint(
    type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_active_user),
):
    """Return workflow steps for the given request type ordered by step order."""

    try:
        return services.get_request_type_steps(db, type_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


# =====================================================
# Request Routes
# Handles employee request submission and retrieval.
# =====================================================


@router.post("/", response_model=schemas.RequestResponse)
def create_request_endpoint(
    data: schemas.RequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new request for the authenticated user."""

    try:
        return services.create_request(
            db,
            current_user,
            request_type_id=data.request_type_id,
            extra_data=data.extra_data,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/my", response_model=list[schemas.RequestResponse])
def get_my_requests_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return requests created by the authenticated user."""

    return services.get_my_requests(db, current_user)


@router.get("/approvals", response_model=list[schemas.ApprovalResponse])
def get_my_approvals_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return pending approval steps currently assigned to the user."""

    return services.get_my_approvals(db, current_user)


# =====================================================
# Approval Action Routes
# Handles approve and reject actions on requests.
# =====================================================


@router.post("/{request_id}/approve", response_model=schemas.ActionResponse)
def approve_request_endpoint(
    request_id: int,
    data: schemas.ApprovalAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve the current request step assigned to the authenticated user."""

    try:
        services.approve_request(db, request_id, current_user, data.comment)
        return {"message": "Request approved successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/{request_id}/reject", response_model=schemas.ActionResponse)
def reject_request_endpoint(
    request_id: int,
    data: schemas.ApprovalAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reject the current request step assigned to the authenticated user."""

    try:
        services.reject_request(db, request_id, current_user, data.comment)
        return {"message": "Request rejected successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
