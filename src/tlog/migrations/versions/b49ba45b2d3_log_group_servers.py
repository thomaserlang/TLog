"""log group servers

Revision ID: b49ba45b2d3
Revises: 1c842a008cac
Create Date: 2013-08-23 17:20:18.601000

"""

# revision identifiers, used by Alembic.
revision = 'b49ba45b2d3'
down_revision = '1c842a008cac'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'log_group_servers',
        sa.Column('name', sa.String(45), primary_key=True),
        sa.Column('log_group_id', sa.Integer(unsigned=True), sa.ForeignKey('log_group.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=True),
        sa.Column('count', sa.Integer(unsigned=True), server_default='0'),
    )


def downgrade():
    op.drop_table('log_group_servers')