"""add user_id to tasks

Revision ID: a1b2c3d4e5f6
Revises: 4d13fc3f415d
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '4d13fc3f415d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Добавляем колонку как nullable, чтобы не упасть на существующих задачах.
    op.add_column(
        'tasks',
        sa.Column(
            'user_id',
            sa.Integer().with_variant(sa.BigInteger(), 'postgresql'),
            nullable=True,
        ),
    )

    # 2. Перепривязываем "осиротевшие" задачи к первому пользователю (если он есть).
    op.execute(
        "UPDATE tasks "
        "SET user_id = (SELECT id FROM users ORDER BY id LIMIT 1) "
        "WHERE user_id IS NULL AND EXISTS (SELECT 1 FROM users)"
    )

    # 3. Удаляем задачи, которые невозможно привязать (пользователей нет вообще).
    op.execute("DELETE FROM tasks WHERE user_id IS NULL")

    # 4. Индекс + внешний ключ.
    op.create_index(op.f('ix_tasks_user_id'), 'tasks', ['user_id'], unique=False)
    op.create_foreign_key(
        'fk_tasks_user_id_users',
        'tasks',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE',
    )

    # 5. Теперь колонка гарантированно заполнена — делаем NOT NULL.
    op.alter_column('tasks', 'user_id', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_tasks_user_id_users', 'tasks', type_='foreignkey')
    op.drop_index(op.f('ix_tasks_user_id'), table_name='tasks')
    op.drop_column('tasks', 'user_id')
