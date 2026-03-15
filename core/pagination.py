from fastapi import Query

# =====================================================
# Pagination Helpers
# Shared helpers for optional limit/offset pagination.
# =====================================================


def limit_query(limit: int | None = Query(default=None, ge=1, le=100)) -> int | None:
    """Return an optional limit value for list endpoints."""

    return limit


def offset_query(offset: int = Query(default=0, ge=0)) -> int:
    """Return an offset value for list endpoints."""

    return offset


def apply_pagination(query, limit: int | None, offset: int):
    """Apply optional limit/offset pagination to a SQLAlchemy query."""

    if offset:
        query = query.offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return query
