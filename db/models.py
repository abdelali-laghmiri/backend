"""Import all SQLAlchemy models so metadata is fully registered."""

import apps.auth.models  # noqa: F401
import apps.permissions.models  # noqa: F401
import apps.organization.models  # noqa: F401
import apps.employees.models  # noqa: F401
import apps.attendance.models  # noqa: F401
import apps.requests.models  # noqa: F401
