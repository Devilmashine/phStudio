"""optimize_indexes

Revision ID: 20250802_optimize_indexes
Revises: 20250716_update_studio_settings_json
Create Date: 2025-08-02 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pathlib import Path

# revision identifiers, used by Alembic
revision = '20250802_optimize_indexes'
down_revision = 'bf1a8a7784e5'
branch_labels = None
depends_on = None

def upgrade():
    # Define SQL statements for SQLite compatibility
    sql_statements = [
        "CREATE INDEX IF NOT EXISTS idx_bookings_date ON bookings (date);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_status ON bookings (status);",
        # "CREATE INDEX IF NOT EXISTS idx_bookings_user_id ON bookings (user_id);", # user_id does not exist
        "CREATE INDEX IF NOT EXISTS idx_bookings_date_status ON bookings (date, status);",
        "CREATE INDEX IF NOT EXISTS idx_bookings_date_time ON bookings (date, start_time, end_time);",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users (email);",
        "CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);",
        # "CREATE INDEX IF NOT EXISTS idx_settings_key ON settings (key);", # settings table does not exist
        # "CREATE INDEX IF NOT EXISTS idx_gallery_category ON gallery_items (category);", # gallery_items does not exist
    ]
    for sql in sql_statements:
        op.execute(sql)

def downgrade():
    # Define SQL statements for dropping indexes
    sql_statements = [
        "DROP INDEX IF EXISTS idx_bookings_date;",
        "DROP INDEX IF EXISTS idx_bookings_status;",
        "DROP INDEX IF EXISTS idx_bookings_date_status;",
        "DROP INDEX IF EXISTS idx_bookings_date_time;",
        "DROP INDEX IF EXISTS idx_users_email;",
        "DROP INDEX IF EXISTS idx_users_role;",
    ]
    for sql in sql_statements:
        op.execute(sql)
