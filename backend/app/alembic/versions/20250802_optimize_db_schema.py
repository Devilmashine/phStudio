"""optimize db schema

Revision ID: 20250802
Revises: bf1a8a7784e5
Create Date: 2025-08-02 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20250802"
down_revision = "bf1a8a7784e5"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Добавляем индексы для оптимизации поиска
    op.create_index(
        "idx_calendar_events_date_range", "calendar_events", ["start_time", "end_time"]
    )
    op.create_index("idx_bookings_date_range", "bookings", ["start_time", "end_time"])

    # 2. Добавляем внешний ключ для связи booking и calendar_event
    op.add_column(
        "bookings",
        sa.Column("calendar_event_id", sa.Integer, sa.ForeignKey("calendar_events.id")),
    )

    # 3. Добавляем поле для кэширования состояния доступности
    op.add_column(
        "calendar_events",
        sa.Column("availability_cached", sa.String(20), nullable=True),
    )
    op.add_column(
        "calendar_events", sa.Column("cache_updated_at", sa.DateTime, nullable=True)
    )

    # 4. Добавляем поле для оптимизации поиска по номеру телефона
    op.add_column(
        "bookings", sa.Column("phone_normalized", sa.String(20), nullable=True)
    )

    # 5. Добавляем индекс для поиска по статусу
    op.create_index("idx_bookings_status", "bookings", ["status"])
    op.create_index("idx_calendar_events_status", "calendar_events", ["status"])


def downgrade():
    op.drop_index("idx_calendar_events_date_range")
    op.drop_index("idx_bookings_date_range")
    op.drop_column("bookings", "calendar_event_id")
    op.drop_column("calendar_events", "availability_cached")
    op.drop_column("calendar_events", "cache_updated_at")
    op.drop_column("bookings", "phone_normalized")
    op.drop_index("idx_bookings_status")
    op.drop_index("idx_calendar_events_status")
