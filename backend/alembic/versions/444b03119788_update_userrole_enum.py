"""update_userrole_enum

Revision ID: 444b03119788
Revises: 0fa2cd70c534
Create Date: 2025-08-30 02:35:59.243015

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '444b03119788'
down_revision: Union[str, None] = 'c138143d1bf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
