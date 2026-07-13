"""rename user_id to creator_id, add assignee_id and assigned_by_id

Revision ID: b7e2f8a9c1d3
Revises: a1b2c3d4e5f6
Create Date: 2026-07-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e2f8a9c1d3'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_USER_ID_TYPE = sa.Integer().with_variant(sa.BigInteger(), 'postgresql')


def upgrade() -> None:
    """Upgrade schema."""
    # 1. user_id -> creator_id (пересоздаём индекс и внешний ключ под новое имя).
    op.drop_constraint('fk_tasks_user_id_users', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.alter_column('tasks', 'user_id', new_column_name='creator_id')
    op.create_index(op.f('ix_tasks_creator_id'), 'tasks', ['creator_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_creator_id_users',
        'tasks',
        'users',
        ['creator_id'],
        ['id'],
        ondelete='CASCADE',
    )

    # 2. Кто выполняет задачу (опционально).
    op.add_column('tasks', sa.Column('assignee_id', _USER_ID_TYPE, nullable=True))
    op.create_index(op.f('ix_tasks_assignee_id'), 'tasks', ['assignee_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_assignee_id_users',
        'tasks',
        'users',
        ['assignee_id'],
        ['id'],
        ondelete='SET NULL',
    )

    # 3. Кто назначил текущего исполнителя (опционально).
    op.add_column('tasks', sa.Column('assigned_by_id', _USER_ID_TYPE, nullable=True))
    op.create_index(op.f('ix_tasks_assigned_by_id'), 'tasks', ['assigned_by_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_assigned_by_id_users',
        'tasks',
        'users',
        ['assigned_by_id'],
        ['id'],
        ondelete='SET NULL',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_tasks_assigned_by_id_users', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_assigned_by_id'), table_name='tasks')
    op.drop_column('tasks', 'assigned_by_id')

    op.drop_constraint('fk_tasks_assignee_id_users', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_assignee_id'), table_name='tasks')
    op.drop_column('tasks', 'assignee_id')

    op.drop_constraint('fk_tasks_creator_id_users', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_creator_id'), table_name='tasks')
    op.alter_column('tasks', 'creator_id', new_column_name='user_id')
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_user_id_users',
        'tasks',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE',
    )
