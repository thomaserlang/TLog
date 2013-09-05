"""filter log groups

Revision ID: 16ad9d43c1cc
Revises: 4c26c44a80c8
Create Date: 2013-08-20 14:52:17.915000

"""

# revision identifiers, used by Alembic.
revision = '16ad9d43c1cc'
down_revision = '4c26c44a80c8'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'filter_log_groups',
        sa.Column('filter_id', sa.Integer(unsigned=True), sa.ForeignKey('filters.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('filter_version', sa.Integer(unsigned=True), primary_key=True, autoincrement=False),
        sa.Column('log_group_id', sa.Integer(unsigned=True), sa.ForeignKey('log_group.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
    )


def downgrade():
    op.drop_table('filter_log_groups')
