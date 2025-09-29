"""fix_booking_legacy_and_status_enum

Revision ID: ce429aede4b3
Revises: d29e37a1c479
Create Date: 2025-09-16 17:40:17.096740

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ce429aede4b3'
down_revision: Union[str, None] = 'd29e37a1c479'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    1. Пересоздаем тип bookingstatus с lowercase значениями
    2. Создаем таблицу bookings_legacy
    3. Копируем данные из bookings в bookings_legacy с конвертацией state в status
    """
    
    # 1. Пересоздаем тип с правильными значениями
    op.execute("""
        DO $$ 
        BEGIN
            -- Всегда пересоздаем тип для уверенности в его значениях
            DROP TYPE IF EXISTS bookingstatus CASCADE;
            CREATE TYPE bookingstatus AS ENUM (
                'pending', 'confirmed', 'cancelled', 'completed'
            );
        END $$;
    """)

    # Удаляем таблицу, если она есть (для idempotent миграции)
    op.execute("DROP TABLE IF EXISTS bookings_legacy CASCADE;")
    # 2. Создаем таблицу bookings_legacy
    op.create_table(
        'bookings_legacy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', postgresql.ENUM('pending', 'confirmed', 'cancelled', 'completed', name='bookingstatus', create_type=False), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('client_name', sa.String(length=200), nullable=False),
        sa.Column('client_phone', sa.String(length=20), nullable=False),
        sa.Column('client_email', sa.String(length=255), nullable=True),
        sa.Column('phone_normalized', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('people_count', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('calendar_event_id', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )    # Создаем индексы
    op.create_index('idx_bookings_legacy_date', 'bookings_legacy', ['date'])
    op.create_index('idx_bookings_legacy_date_range', 'bookings_legacy', ['start_time', 'end_time'])
    op.create_index('idx_bookings_legacy_status', 'bookings_legacy', ['status'])
    op.create_index('idx_bookings_legacy_client_phone', 'bookings_legacy', ['client_phone'])
    op.create_index('idx_bookings_legacy_phone_normalized', 'bookings_legacy', ['phone_normalized'])
    op.create_index('idx_bookings_legacy_created_at', 'bookings_legacy', ['created_at'])
    
    # 3. Копируем данные из bookings в bookings_legacy с конвертацией state в status
    op.execute("""
        INSERT INTO bookings_legacy (
            date,
            start_time,
            end_time,
            status,
            total_price,
            client_name,
            client_phone,
            client_email,
            phone_normalized,
            notes,
            people_count,
            created_at,
            updated_at,
            calendar_event_id
        )
        SELECT 
            booking_date,
            start_time,
            end_time,
            CASE state::text
                WHEN 'pending' THEN 'pending'::bookingstatus
                WHEN 'confirmed' THEN 'confirmed'::bookingstatus
                WHEN 'cancelled' THEN 'cancelled'::bookingstatus
                WHEN 'completed' THEN 'completed'::bookingstatus
                ELSE 'pending'::bookingstatus
            END as status,
            total_price,
            client_name,
            client_phone,
            client_email,
            client_phone_normalized,
            notes,
            people_count,
            created_at,
            updated_at,
            calendar_event_id::integer
        FROM bookings b
        WHERE NOT EXISTS (
            -- Проверяем, что такой записи еще нет (избегаем дубликатов)
            SELECT 1 FROM bookings_legacy bl
            WHERE bl.start_time = b.start_time 
            AND bl.end_time = b.end_time
            AND bl.client_phone = b.client_phone
        );
    """)


def downgrade() -> None:
    """
    При откате удаляем созданную таблицу bookings_legacy
    """
    op.execute("DROP TABLE IF EXISTS bookings_legacy;")
    # Не удаляем тип bookingstatus, так как он может использоваться в других местах
