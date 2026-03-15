from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from db.base import Base

# =====================================================
# Attendance Models
# Stores employee check-in and check-out history.
# =====================================================


class Attendance(Base):
    """Single attendance punch record for an employee."""

    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False, index=True)
    check_in = Column(DateTime(timezone=True), nullable=False)
    check_out = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    employee = relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        CheckConstraint(
            "check_out IS NULL OR check_out > check_in",
            name="ck_attendance_checkout_after_checkin",
        ),
    )
