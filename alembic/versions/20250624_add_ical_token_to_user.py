"""
Alembic migration script to add ical_token field to users table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250624_add_ical_token_to_user'
down_revision = '47065ec3032b'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('ical_token', sa.String(length=64), nullable=True))
        batch_op.create_unique_constraint('uq_users_ical_token', ['ical_token'])

def downgrade():
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_users_ical_token', type_='unique')
        batch_op.drop_column('ical_token')
