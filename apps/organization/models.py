import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from apps.permissions.models import JobTitlePermission
from apps.requests.models import ApprovalStep
from db.base import Base

# =====================================================
# Organization Models
# Represents the company structure and reporting scopes.
# =====================================================


class PositionScope(str, enum.Enum):
    """Defines how far a job title's authority or visibility applies."""

    NONE = "NONE"
    TEAM = "TEAM"
    DEPARTMENT = "DEPARTMENT"
    GLOBAL = "GLOBAL"


class JobTitle(Base):
    """Catalog entry for employee job titles and their approval scope."""

    __tablename__ = "job_titles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    scope = Column(Enum(PositionScope), nullable=False)
    level = Column(Integer, nullable=False)

    description = Column(String, nullable=True)

    monthly_leave_accrual = Column(Float, nullable=False, default=0.0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    employees = relationship("Employee", back_populates="job_title")
    permission_assignments = relationship(
        JobTitlePermission,
        back_populates="job_title",
        cascade="all, delete-orphan",
    )
    approval_steps = relationship(ApprovalStep, back_populates="job_title")


class Department(Base):
    """Top-level organizational unit that groups multiple teams."""

    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)

    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    manager = relationship(
        "User",
        back_populates="managed_departments",
        foreign_keys=[manager_id],
    )
    teams = relationship("Team", back_populates="department", cascade="all, delete")
    employees = relationship("Employee", back_populates="department")


class Team(Base):
    """Subdivision of a department with an optional team leader."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    team_leader_id = Column(Integer, ForeignKey("users.id"), nullable=True)


    department = relationship("Department", back_populates="teams")
    team_leader = relationship(
        "User",
        back_populates="led_teams",
        foreign_keys=[team_leader_id],
    )
    employees = relationship("Employee", back_populates="team")

    __table_args__ = (
        UniqueConstraint("department_id", "name", name="uix_department_team"),
    )
