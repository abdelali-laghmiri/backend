from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# =====================================================
# Authentication Models
# Defines users and their system-wide roles.
# =====================================================

# impoert the Base class from your database setup
from db.base import Base

# Define an enum for user roles
class UserRole(enum.Enum):
    """Supported roles for application users."""

    USER = "user"
    SUPERUSER = "superuser"

# Define the User model
class User(Base):
    """Primary user account used for authentication and ownership."""

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricule =  Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    first_login = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    managed_departments = relationship("Department", back_populates="manager")
    led_teams = relationship("Team", back_populates="team_leader")
    employee = relationship("Employee", back_populates="user", uselist=False)
