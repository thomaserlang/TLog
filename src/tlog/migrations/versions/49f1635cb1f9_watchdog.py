"""watchdog

Revision ID: 49f1635cb1f9
Revises: 278fee33e24b
Create Date: 2013-08-30 12:32:44.623000

"""

# revision identifiers, used by Alembic.
revision = '49f1635cb1f9'
down_revision = '278fee33e24b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'watchdog',
        sa.Column('id', sa.Integer(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('heartbeat', sa.TIMESTAMP),
    )


def downgrade():
    op.drop_table('watchdog')
