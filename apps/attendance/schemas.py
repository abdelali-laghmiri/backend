from datetime import datetime

from pydantic import BaseModel, ConfigDict

# =====================================================
# Attendance Schemas
# Pydantic models for employee attendance actions and reads.
# =====================================================


class AttendanceResponse(BaseModel):
    """Serialized attendance record."""

    id: int
    employee_id: int
    check_in: datetime
    check_out: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
