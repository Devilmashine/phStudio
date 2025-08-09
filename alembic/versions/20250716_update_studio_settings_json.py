"""update studio_settings work_days and holidays to JSON string fields

Revision ID: 20250716_update_studio_settings_json
Revises: 8931d0d28486
Create Date: 2025-07-16 15:00:00.000000
"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = '20250716_update_studio_settings_json'
down_revision: Union[str, Sequence[str], None] = '8931d0d28486'
branch_labels = None
depends_on = None
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.alter_column('studio_settings', 'work_days', type_=sa.String(length=1024), existing_type=sa.String(length=255), existing_nullable=False)
    op.alter_column('studio_settings', 'holidays', type_=sa.String(length=1024), existing_type=sa.String(length=1024), existing_nullable=True)

def downgrade():
    op.alter_column('studio_settings', 'work_days', type_=sa.String(length=255), existing_type=sa.String(length=1024), existing_nullable=False)
    op.alter_column('studio_settings', 'holidays', type_=sa.String(length=1024), existing_type=sa.String(length=1024), existing_nullable=True)
