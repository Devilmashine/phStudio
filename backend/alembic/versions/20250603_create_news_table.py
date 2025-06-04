"""create news table

Revision ID: 20250603_create_news_table
Revises: 
Create Date: 2025-06-03

"""
from alembic import op
import sqlalchemy as sa

description = 'Создание таблицы news для CRUD новостей'

revision = '20250603_create_news_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'news',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('published_at', sa.DateTime, nullable=True),
        sa.Column('author_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('status', sa.String(32), nullable=False, default='draft'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

def downgrade():
    op.drop_table('news')
