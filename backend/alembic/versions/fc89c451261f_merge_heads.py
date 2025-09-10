"""Merge heads

Revision ID: fc89c451261f
Revises: 9dffd58f1abe, aeb67ca86145
Create Date: 2025-09-02 01:28:27.646624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc89c451261f'
down_revision: Union[str, None] = ('9dffd58f1abe', 'aeb67ca86145')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
