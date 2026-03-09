from sqlalchemy import Column, Integer, String, ForeignKey
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


class JobTitlePermission(Base):
    """Association between a job title and a permission."""

    __tablename__ = "job_title_permissions"

    id = Column(Integer, primary_key=True)

    job_title_id = Column(Integer, ForeignKey("job_titles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)

    permission = relationship("Permission")
