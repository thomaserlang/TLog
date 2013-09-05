"""filter log_group notification

Revision ID: 278fee33e24b
Revises: b49ba45b2d3
Create Date: 2013-08-28 15:59:38.275000

"""

# revision identifiers, used by Alembic.
revision = '278fee33e24b'
down_revision = 'b49ba45b2d3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'filter_notification_last_sent',
        sa.Column('filter_id', sa.Integer(unsigned=True), sa.ForeignKey('filters.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('last_sent', sa.TIMESTAMP),
    )

    op.create_table(
        'log_group_notification_last_sent',
        sa.Column('log_group_id', sa.Integer(unsigned=True), sa.ForeignKey('log_group.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('last_sent', sa.TIMESTAMP),
    )


def downgrade():
    op.drop_table('filter_notification_last_sent')
    op.drop_table('log_group_notification_last_sent')
