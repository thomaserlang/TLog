"""web sessions

Revision ID: 80419eace79
Revises: 4b3e2f332045
Create Date: 2013-08-22 09:06:42.774000

"""

# revision identifiers, used by Alembic.
revision = '80419eace79'
down_revision = '4b3e2f332045'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'web_sessions',
        sa.Column('session', sa.String(100), primary_key=True, autoincrement=False),
        sa.Column('user_id', sa.Integer(unsigned=True), sa.ForeignKey('users.id', onupdate="cascade", ondelete="cascade")),
        sa.Column('expires', sa.TIMESTAMP),
    )

def downgrade():
    op.drop_table('web_sessions')
