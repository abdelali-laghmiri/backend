"""create requests workflow tables

Revision ID: 3f8c2b7a1d90
Revises: e9cabbf64a86
Create Date: 2026-03-09 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3f8c2b7a1d90"
down_revision: Union[str, Sequence[str], None] = "e9cabbf64a86"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "request_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_request_types_id"), "request_types", ["id"], unique=False)

    op.create_table(
        "request_type_fields",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_type_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column(
            "field_type",
            sa.Enum(
                "TEXT",
                "TEXTAREA",
                "NUMBER",
                "DATE",
                "DATETIME",
                "SELECT",
                "BOOLEAN",
                "FILE",
                name="requestfieldtype",
            ),
            nullable=False,
        ),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("placeholder", sa.String(), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("field_order", sa.Integer(), nullable=False),
        sa.Column("default_value", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["request_type_id"], ["request_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_type_id", "field_order", name="uix_request_type_field_order"),
        sa.UniqueConstraint("request_type_id", "name", name="uix_request_type_field_name"),
    )
    op.create_index(op.f("ix_request_type_fields_id"), "request_type_fields", ["id"], unique=False)

    op.create_table(
        "approval_steps",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_type_id", sa.Integer(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("job_title_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["job_title_id"], ["job_titles.id"]),
        sa.ForeignKeyConstraint(["request_type_id"], ["request_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("request_type_id", "step_order", name="uix_request_step_order"),
    )
    op.create_index(op.f("ix_approval_steps_id"), "approval_steps", ["id"], unique=False)

    op.create_table(
        "requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("request_type_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="requeststatus"),
            nullable=False,
        ),
        sa.Column("current_step", sa.Integer(), nullable=True),
        sa.Column("extra_data", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=True),
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"]),
        sa.ForeignKeyConstraint(["request_type_id"], ["request_types.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_requests_id"), "requests", ["id"], unique=False)

    op.create_table(
        "request_approvals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("approver_user_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "APPROVED", "REJECTED", name="approvalstatus"),
            nullable=False,
        ),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["approver_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_request_approvals_id"), "request_approvals", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_request_approvals_id"), table_name="request_approvals")
    op.drop_table("request_approvals")

    op.drop_index(op.f("ix_requests_id"), table_name="requests")
    op.drop_table("requests")

    op.drop_index(op.f("ix_approval_steps_id"), table_name="approval_steps")
    op.drop_table("approval_steps")

    op.drop_index(op.f("ix_request_type_fields_id"), table_name="request_type_fields")
    op.drop_table("request_type_fields")

    op.drop_index(op.f("ix_request_types_id"), table_name="request_types")
    op.drop_table("request_types")
