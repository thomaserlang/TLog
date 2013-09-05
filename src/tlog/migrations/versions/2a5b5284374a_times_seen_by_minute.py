"""times seen by minute

Revision ID: 2a5b5284374a
Revises: 1af1b6c81491
Create Date: 2013-08-20 09:39:26.179000

"""

# revision identifiers, used by Alembic.
revision = '2a5b5284374a'
down_revision = '1af1b6c81491'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'filters',
        sa.Column('id', sa.Integer(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('version', sa.Integer(unsigned=True), server_default='1'),
        sa.Column('name', sa.String(45)),
        sa.Column('data', sa.Text),
    )

    op.create_table(
        'filter_versions',
        sa.Column('filter_id', sa.Integer(unsigned=True), sa.ForeignKey('filters.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('version', sa.Integer(unsigned=True), primary_key=True, autoincrement=False),
        sa.Column('data', sa.Text),
    )

    op.create_table(
        'filter_teams',
        sa.Column('filter_id', sa.Integer(unsigned=True), sa.ForeignKey('filters.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('team_id', sa.Integer(unsigned=True), sa.ForeignKey('teams.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
    )

    op.create_table(
        'times_seen_by_minute',
        sa.Column('time', sa.DateTime, primary_key=True, autoincrement=False),
        sa.Column('log_group_id', sa.Integer(unsigned=True), sa.ForeignKey('log_group.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('filter_id', sa.Integer(unsigned=True), sa.ForeignKey('filters.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('times_seen', sa.Integer(unsigned=True), server_default='0')
    )
    op.create_index('ix_time', 'times_seen_by_minute', ['time'])

def downgrade():
    op.drop_table('times_seen_by_minute')
    op.drop_table('filter_teams')
    op.drop_table('filter_versions')
    op.drop_table('filters')
