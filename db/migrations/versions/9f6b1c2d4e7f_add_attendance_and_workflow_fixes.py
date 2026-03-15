"""add attendance and workflow fixes

Revision ID: 9f6b1c2d4e7f
Revises: c5f9f4e6a2b1
Create Date: 2026-03-15 01:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f6b1c2d4e7f"
down_revision: Union[str, Sequence[str], None] = "c5f9f4e6a2b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(bind, table_name: str) -> bool:
    return table_name in sa.inspect(bind).get_table_names()


def _has_column(bind, table_name: str, column_name: str) -> bool:
    return any(
        column["name"] == column_name
        for column in sa.inspect(bind).get_columns(table_name)
    )


def _has_unique_constraint(bind, table_name: str, constraint_name: str) -> bool:
    return any(
        constraint["name"] == constraint_name
        for constraint in sa.inspect(bind).get_unique_constraints(table_name)
    )


def _delete_duplicate_job_title_permissions(bind) -> None:
    job_title_permissions = sa.table(
        "job_title_permissions",
        sa.column("id", sa.Integer()),
        sa.column("job_title_id", sa.Integer()),
        sa.column("permission_id", sa.Integer()),
    )

    rows = bind.execute(
        sa.select(
            job_title_permissions.c.id,
            job_title_permissions.c.job_title_id,
            job_title_permissions.c.permission_id,
        ).order_by(
            job_title_permissions.c.job_title_id,
            job_title_permissions.c.permission_id,
            job_title_permissions.c.id,
        )
    ).fetchall()

    seen: set[tuple[int, int]] = set()
    duplicate_ids: list[int] = []

    for row in rows:
        key = (row.job_title_id, row.permission_id)
        if key in seen:
            duplicate_ids.append(row.id)
            continue
        seen.add(key)

    if duplicate_ids:
        bind.execute(
            sa.delete(job_title_permissions).where(
                job_title_permissions.c.id.in_(duplicate_ids)
            )
        )


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()

    if not _has_table(bind, "attendances"):
        op.create_table(
            "attendances",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("employee_id", sa.Integer(), nullable=False),
            sa.Column("check_in", sa.DateTime(timezone=True), nullable=False),
            sa.Column("check_out", sa.DateTime(timezone=True), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.CheckConstraint(
                "check_out IS NULL OR check_out > check_in",
                name="ck_attendance_checkout_after_checkin",
            ),
            sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_attendances_employee_id"), "attendances", ["employee_id"], unique=False)
        op.create_index(op.f("ix_attendances_id"), "attendances", ["id"], unique=False)

    if _has_table(bind, "request_approvals") and not _has_column(bind, "request_approvals", "comment"):
        with op.batch_alter_table("request_approvals") as batch_op:
            batch_op.add_column(sa.Column("comment", sa.Text(), nullable=True))

    if _has_table(bind, "job_title_permissions") and not _has_unique_constraint(
        bind,
        "job_title_permissions",
        "uix_job_title_permission_assignment",
    ):
        _delete_duplicate_job_title_permissions(bind)
        with op.batch_alter_table("job_title_permissions") as batch_op:
            batch_op.create_unique_constraint(
                "uix_job_title_permission_assignment",
                ["job_title_id", "permission_id"],
            )


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()

    if _has_table(bind, "job_title_permissions") and _has_unique_constraint(
        bind,
        "job_title_permissions",
        "uix_job_title_permission_assignment",
    ):
        with op.batch_alter_table("job_title_permissions") as batch_op:
            batch_op.drop_constraint(
                "uix_job_title_permission_assignment",
                type_="unique",
            )

    if _has_table(bind, "request_approvals") and _has_column(bind, "request_approvals", "comment"):
        with op.batch_alter_table("request_approvals") as batch_op:
            batch_op.drop_column("comment")

    if _has_table(bind, "attendances"):
        op.drop_index(op.f("ix_attendances_id"), table_name="attendances")
        op.drop_index(op.f("ix_attendances_employee_id"), table_name="attendances")
        op.drop_table("attendances")
