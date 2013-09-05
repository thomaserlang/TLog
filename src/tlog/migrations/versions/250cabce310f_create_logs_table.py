"""create logs table

Revision ID: 250cabce310f
Revises: None
Create Date: 2013-08-13 19:30:09.263000

"""

# revision identifiers, used by Alembic.
revision = '250cabce310f'
down_revision = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'log_group',
        sa.Column('id', sa.Integer(unsigned=True), autoincrement=True, primary_key=True),
        sa.Column('message', sa.String(200)),
        sa.Column('message_hash', sa.String(40), unique=True),
        sa.Column('first_seen', sa.TIMESTAMP),
        sa.Column('last_seen', sa.TIMESTAMP, index=True),
        sa.Column('last_log_id', sa.Integer(unsigned=True)),
        sa.Column('times_seen', sa.Integer(unsigned=True), nullable=False, server_default='0'),
        sa.Column('level', sa.Integer(unsigned=True)),
        sa.Column('score', sa.Integer(unsigned=True), index=True),
        sa.Column('status', sa.Integer(unsigned=True), server_default='0'),
        sa.Column('reopened', sa.TIMESTAMP),           
    )

    op.create_table(
        'logs',
        sa.Column(
            'id', 
            sa.Integer(unsigned=True), 
            primary_key=True, 
            autoincrement=True,
        ),
        sa.Column(
            'external_id',
            sa.String(32),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            'received',
            sa.TIMESTAMP,
        ),
        sa.Column(
            'message_hash',
            sa.String(40),
        ),
        sa.Column(
            'data',
            sa.Text,
        ),
        sa.Column(
            'hostname',
            sa.String(45),
        ),
        sa.Column(
            'level',
            sa.Integer(unsigned=True),
            nullable=False,
        ),
        sa.Column('log_group_id', sa.Integer(unsigned=True), sa.ForeignKey('log_group.id', onupdate='cascade', ondelete='cascade')),
    )
    op.create_index('ix_message_hash', 'logs', ['message_hash'])
    op.create_index('ix_hostname', 'logs', ['hostname'])
    op.create_index('ix_level', 'logs', ['level'])

def downgrade():
    op.drop_table('logs')
    op.drop_table('log_group')
