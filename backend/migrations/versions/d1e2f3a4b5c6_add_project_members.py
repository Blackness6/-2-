"""add project_members table

Revision ID: d1e2f3a4b5c6
Revises: c8f3a1b6d4e2
Create Date: 2026-07-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd1e2f3a4b5c6'
down_revision: Union[str, Sequence[str], None] = 'c8f3a1b6d4e2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ID_TYPE = sa.Integer().with_variant(sa.BigInteger(), 'postgresql')


def upgrade() -> None:
    op.create_table(
        'project_members',
        sa.Column('id', _ID_TYPE, autoincrement=True, nullable=False),
        sa.Column('project_id', _ID_TYPE, nullable=False),
        sa.Column('user_id', _ID_TYPE, nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_project_members'),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.id'],
            name='fk_project_members_project_id_projects', ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['user_id'], ['users.id'],
            name='fk_project_members_user_id_users', ondelete='CASCADE',
        ),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_members_project_user'),
    )
    op.create_index(op.f('ix_project_members_project_id'), 'project_members', ['project_id'], unique=False)
    op.create_index(op.f('ix_project_members_user_id'), 'project_members', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_project_members_user_id'), table_name='project_members')
    op.drop_index(op.f('ix_project_members_project_id'), table_name='project_members')
    op.drop_table('project_members')