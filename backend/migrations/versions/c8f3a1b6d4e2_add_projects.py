"""add projects table and project_id to tasks

Revision ID: c8f3a1b6d4e2
Revises: b7e2f8a9c1d3
Create Date: 2026-07-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8f3a1b6d4e2'
down_revision: Union[str, Sequence[str], None] = 'b7e2f8a9c1d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_ID_TYPE = sa.Integer().with_variant(sa.BigInteger(), 'postgresql')


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Таблица проектов.
    op.create_table(
        'projects',
        sa.Column('id', _ID_TYPE, autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', _ID_TYPE, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id', name='pk_projects'),
        sa.ForeignKeyConstraint(
            ['owner_id'],
            ['users.id'],
            name='fk_projects_owner_id_users',
            ondelete='CASCADE',
        ),
    )
    op.create_index(op.f('ix_projects_owner_id'), 'projects', ['owner_id'], unique=False)

    # 2. Привязка задачи к проекту (опционально).
    op.add_column('tasks', sa.Column('project_id', _ID_TYPE, nullable=True))
    op.create_index(op.f('ix_tasks_project_id'), 'tasks', ['project_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_project_id_projects',
        'tasks',
        'projects',
        ['project_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_tasks_project_id_projects', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_project_id'), table_name='tasks')
    op.drop_column('tasks', 'project_id')

    op.drop_index(op.f('ix_projects_owner_id'), table_name='projects')
    op.drop_table('projects')
