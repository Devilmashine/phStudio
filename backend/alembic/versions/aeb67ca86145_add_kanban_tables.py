"""Add Kanban tables

Revision ID: aeb67ca86145
Revises: 9dffd58f1abe
Create Date: 2025-08-29 18:55:14.561771

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aeb67ca86145'
down_revision: Union[str, None] = '0fa2cd70c534'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
