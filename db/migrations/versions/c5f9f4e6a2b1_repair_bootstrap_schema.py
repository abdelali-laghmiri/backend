"""repair bootstrap schema

Revision ID: c5f9f4e6a2b1
Revises: 3f8c2b7a1d90
Create Date: 2026-03-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5f9f4e6a2b1'
down_revision: Union[str, Sequence[str], None] = '3f8c2b7a1d90'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_table(bind, table_name: str) -> bool:
    return table_name in sa.inspect(bind).get_table_names()


def upgrade() -> None:
    """Backfill schema objects for environments that used create_all or empty revisions."""
    bind = op.get_bind()

    if not _has_table(bind, 'users'):
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('matricule', sa.String(), nullable=False),
            sa.Column('hashed_password', sa.String(), nullable=False),
            sa.Column('role', sa.Enum('USER', 'SUPERUSER', name='userrole'), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False),
            sa.Column('first_login', sa.Boolean(), server_default=sa.true(), nullable=False),
            sa.Column(
                'created_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=True,
            ),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
        op.create_index(op.f('ix_users_matricule'), 'users', ['matricule'], unique=True)

    if not _has_table(bind, 'permissions'):
        op.create_table(
            'permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=False),
            sa.Column('description', sa.String(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name'),
        )
        op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)

    if not _has_table(bind, 'job_title_permissions'):
        op.create_table(
            'job_title_permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('job_title_id', sa.Integer(), nullable=False),
            sa.Column('permission_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['job_title_id'], ['job_titles.id']),
            sa.ForeignKeyConstraint(['permission_id'], ['permissions.id']),
            sa.PrimaryKeyConstraint('id'),
        )

    if bind.dialect.name == 'postgresql' and _has_table(bind, 'job_titles'):
        op.execute("ALTER TYPE positionscope ADD VALUE IF NOT EXISTS 'NONE'")


def downgrade() -> None:
    """This repair migration is intentionally irreversible."""
    pass
