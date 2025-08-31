"""add_booking_lock_time

Revision ID: 20250830_add_booking_lock_time
Revises: 444b03119788
Create Date: 2025-08-30 01:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20250830_add_booking_lock_time'
down_revision: Union[str, None] = '444b03119788'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if booking_lock_time column exists before adding it
    from sqlalchemy import text
    conn = op.get_bind()
    result = conn.execute(text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='studio_settings' AND column_name='booking_lock_time'
    """)).fetchone()
    
    # Add booking_lock_time column to studio_settings table if it doesn't exist
    if not result:
        op.add_column('studio_settings', sa.Column('booking_lock_time', sa.Integer(), nullable=True))
        # Set default value
        op.execute("UPDATE studio_settings SET booking_lock_time = 2")


def downgrade() -> None:
    # Remove booking_lock_time column from studio_settings table
    op.drop_column('studio_settings', 'booking_lock_time')