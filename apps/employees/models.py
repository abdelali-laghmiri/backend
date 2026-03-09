from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from db.base import Base

from apps.organization.models import Department, Team, JobTitle
from apps.auth.models import User
from enum import Enum as PyEnum

# =====================================================
# Employee Models
# Stores the HR profile linked to each authenticated user.
# =====================================================


class EmploymentStatus(str, PyEnum):
    """Lifecycle status of an employee in the company."""

    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"

class Employee(Base):
    """Employee profile linked to organizational assignments and a user account."""

    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)

    # 1️⃣ One-to-One with User
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)

    hire_date = Column(Date, nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    job_title_id = Column(Integer, ForeignKey("job_titles.id"), nullable=False, index=True)

    current_leave_balance = Column(Integer, default=0)

    employment_status = Column(Enum(EmploymentStatus),default=EmploymentStatus.ACTIVE,nullable=False)

    # Relationships
    user = relationship("User", back_populates="employee")
    department = relationship("Department")
    team = relationship("Team")
    job_title = relationship("JobTitle")
