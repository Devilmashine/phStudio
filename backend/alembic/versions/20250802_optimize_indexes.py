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
down_revision = '20250716_update_studio_settings_json'
branch_labels = None
depends_on = None

def upgrade():
    # Читаем SQL-файл и выполняем его
    sql_file = Path(__file__).parent / '20250802_optimize_indexes.sql'
    with sql_file.open() as f:
        sql = f.read()
        op.execute(sql)

def downgrade():
    # Удаляем созданные индексы
    op.execute("""
        DROP INDEX IF EXISTS idx_bookings_date;
        DROP INDEX IF EXISTS idx_bookings_status;
        DROP INDEX IF EXISTS idx_bookings_user_id;
        DROP INDEX IF EXISTS idx_bookings_date_status;
        DROP INDEX IF EXISTS idx_bookings_date_time;
        DROP INDEX IF EXISTS idx_users_email;
        DROP INDEX IF EXISTS idx_users_role;
        DROP INDEX IF EXISTS idx_settings_key;
        DROP INDEX IF EXISTS idx_gallery_category;
        DROP INDEX IF EXISTS idx_gallery_tags;
        DROP INDEX IF EXISTS idx_bookings_search;
        DROP INDEX IF EXISTS idx_bookings_time_range;
    """)
