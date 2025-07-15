"""merge ical_token and studio_settings branches

Revision ID: ca07d47c96b0
Revises: c6e2698855bd, 20250624_add_ical_token_to_user
Create Date: 2025-06-24 20:05:48.093783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ca07d47c96b0'
down_revision: Union[str, None] = ('c6e2698855bd', '20250624_add_ical_token_to_user')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
