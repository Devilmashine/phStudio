"""create studio_settings table

Revision ID: c6e2698855bd
Revises: 8f1ded96c4dd
Create Date: 2025-06-04 09:31:16.405352

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c6e2698855bd'
down_revision: Union[str, None] = '8f1ded96c4dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Удалён ALTER COLUMN для SQLite. Создаём таблицу studio_settings.
    op.create_table(
        'studio_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=255), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # Удаляем таблицу studio_settings при откате миграции
    op.drop_table('studio_settings')
    # ### end Alembic commands ###
