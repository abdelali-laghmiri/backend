from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.auth.models import User
from apps.permissions.dependencies import require_permission
from apps.permissions.schemas import (
    JobTitlePermissionAssign,
    JobTitlePermissionResponse,
    PermissionActionResponse,
    PermissionResponse,
)
from apps.permissions.services import (
    assign_permission_to_job_title,
    list_job_title_permissions,
    list_permissions,
    remove_permission_from_job_title,
)
from db.session import get_db

router = APIRouter(prefix="/permissions", tags=["Permissions"])

# =====================================================
# Permissions Router
# Exposes permission listing and job title assignment APIs.
# =====================================================


@router.get("/", response_model=list[PermissionResponse])
def list_permissions_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permissions.read")),
):
    """List all available permissions."""

    return list_permissions(db)


@router.get("/job-titles/{job_title_id}", response_model=list[JobTitlePermissionResponse])
def list_job_title_permissions_endpoint(
    job_title_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permissions.read")),
):
    """List permissions assigned to a job title."""

    try:
        return list_job_title_permissions(db, job_title_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post("/job-titles/{job_title_id}", response_model=JobTitlePermissionResponse)
def assign_permission_endpoint(
    job_title_id: int,
    data: JobTitlePermissionAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permissions.assign")),
):
    """Assign a permission to a job title."""

    try:
        return assign_permission_to_job_title(db, job_title_id, data.permission_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/job-titles/{job_title_id}/{permission_id}",
    response_model=PermissionActionResponse,
)
def remove_permission_endpoint(
    job_title_id: int,
    permission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("permissions.assign")),
):
    """Remove a permission assignment from a job title."""

    try:
        remove_permission_from_job_title(db, job_title_id, permission_id)
        return {"message": "Permission removed from job title successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
