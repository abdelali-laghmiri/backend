from sqlalchemy import Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base import Base

# =====================================================
# Permission Models
# Maps job titles to reusable permission entries.
# =====================================================


class Permission(Base):
    """Named permission that can be assigned to job titles."""

    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    job_title_assignments = relationship(
        "JobTitlePermission",
        back_populates="permission",
        cascade="all, delete-orphan",
    )


class JobTitlePermission(Base):
    """Association between a job title and a permission."""

    __tablename__ = "job_title_permissions"

    id = Column(Integer, primary_key=True)

    job_title_id = Column(Integer, ForeignKey("job_titles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    job_title = relationship("JobTitle", back_populates="permission_assignments")
    permission = relationship("Permission", back_populates="job_title_assignments")

    __table_args__ = (
        UniqueConstraint(
            "job_title_id",
            "permission_id",
            name="uix_job_title_permission_assignment",
        ),
    )
