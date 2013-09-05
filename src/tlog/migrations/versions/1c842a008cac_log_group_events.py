"""log_group_events

Revision ID: 1c842a008cac
Revises: 80419eace79
Create Date: 2013-08-23 12:06:14.647000

"""

# revision identifiers, used by Alembic.
revision = '1c842a008cac'
down_revision = '80419eace79'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'log_group_events',
        sa.Column('id', sa.Integer(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('log_group_id', sa.Integer(unsigned=True), sa.ForeignKey('log_group.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('user_id', sa.Integer(unsigned=True), sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade')),
        sa.Column('message', sa.String(200)),
        sa.Column('time', sa.TIMESTAMP),
    )

def downgrade():
    op.drop_table('log_group_events')
