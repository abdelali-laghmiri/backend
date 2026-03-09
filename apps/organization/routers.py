from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from apps.organization.models import JobTitle,Team

from db.session import get_db
from apps.organization.schemas import (
    JobTitleCreate, 
    JobTitleResponse,
    DepartmentResponse,
    DepartmentCreate,
    TeamResponse,
    TeamCreate,
)
from apps.organization.services import (
    create_job_title,
    delete_job_title,
    create_department,
    list_departments,
    get_teams_by_department,
    delete_department,
    create_team,
    list_teams,
    delete_team
)

from apps.auth.dependencies import require_superuser, require_active_user


router = APIRouter(prefix="/organization", tags=["Organization"])

# =====================================================
# Organization Router
# Exposes endpoints for job titles, departments, and teams.
# =====================================================

  
#=================== job-titles routers ==================================#
@router.post("/job-titels",response_model=JobTitleResponse)
def create_job_title_endpoint(
    data: JobTitleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_superuser),
):
    """Create a job title. Restricted to superusers."""
    try:
        job_title = create_job_title(db, data)
        return job_title
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
@router.get("/job-titles", response_model=list[JobTitleResponse])
def list_job_titles(
    db: Session = Depends(get_db),
    current_user = Depends(require_active_user),
):
    """List all available job titles."""
    return db.query(JobTitle).all()
@router.delete("/job-titles/{job_title_id}")
def delete_job_title_endpoint(
    job_title_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_superuser),
):
    """Delete a job title. Restricted to superusers."""
    try:
        delete_job_title(db, job_title_id)
        return {"message": "Job title deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
#=================== end  job-titles routers =============================#


# =========================== department routers  ============================================
@router.post("/departments", response_model=DepartmentResponse)
def create_department_endpoint(
    data: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_superuser),
):
    """Create a department. Restricted to superusers."""
    try:
        return create_department(
            db,
            name=data.name,
            description=data.description,
            manager_id=data.manager_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )
@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(require_active_user),
):
    """List departments with their related structure."""
    return list_departments(db)
@router.delete("/departments/{department_id}")
def delete_department_endpoint(
    department_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_superuser),
):
    """Delete a department. Restricted to superusers."""
    try:
        delete_department(db, department_id)
        return {"message": "Department deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
#=========================== end ====================================================
#=========================== start teams routers ====================================
@router.post("/teams", response_model=TeamResponse)
def create_team_endpoint(
    data: TeamCreate,
    db: Session = Depends(get_db),
    current_user = Depends(require_superuser),
):
    """Create a team. Restricted to superusers."""
    try:
        return create_team(
            db,
            name=data.name,
            department_id=data.department_id,
            team_leader_id=data.team_leader_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/teams", response_model=list[TeamResponse])
def list_teams_endpoint(
    db: Session = Depends(get_db),
    current_user = Depends(require_active_user),
):
    """List all teams."""
    return list_teams(db)
@router.delete("/teams/{team_id}")
def delete_team_endpoint(
    team_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_superuser),
):
    """Delete a team. Restricted to superusers."""
    try:
        delete_team(db, team_id)
        return {"message": "Team deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
#=============================== end ================================================
@router.get("/departments/{department_id}/teams", response_model=list[TeamResponse])
def get_department_teams(
    department_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(require_active_user),
):
    """List teams that belong to the specified department."""
    try:
        return get_teams_by_department(db, department_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
