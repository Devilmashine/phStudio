"""add_employees_table

Revision ID: 0fa2cd70c534
Revises: 20250830_add_booking_lock_time
Create Date: 2025-08-30 01:58:36.713904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fa2cd70c534'
down_revision: Union[str, None] = '20250830_add_booking_lock_time'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
