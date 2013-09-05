"""create teams table

Revision ID: 54168b4b9302
Revises: 250cabce310f
Create Date: 2013-08-17 16:55:31.792000

"""

# revision identifiers, used by Alembic.
revision = '54168b4b9302'
down_revision = '250cabce310f'

from alembic import op
import sqlalchemy as sa
import getpass
from tlog.base.user import User
from sqlalchemy.orm import sessionmaker
from tlog.connections import Database

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('email', sa.String(45), nullable=False, unique=True),
        sa.Column('password', sa.CHAR(60)),
        sa.Column('name', sa.String(45)),
        sa.Column('notification_types', sa.Text),
    )

    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(unsigned=True), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(45), unique=True),
    )

    op.create_table(
        'user_teams',
        sa.Column('user_id', sa.Integer(unsigned=True), sa.ForeignKey('users.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
        sa.Column('team_id', sa.Integer(unsigned=True), sa.ForeignKey('teams.id', onupdate='cascade', ondelete='cascade'), primary_key=True, autoincrement=False),
    )

    op.create_unique_constraint('uq_user_id_team_id', 'user_teams', ['user_id', 'team_id'])

    # create a system user
    User.new(
        name='TLOG',
        email='tlog@example.com',
    )

    # create a admin user
    need_info = True
    while need_info:
        print 'An admin user needs to be set up.'
        name = raw_input("Name: ")
        if name:
            email = raw_input("Email address: ")
            if email:
                password = getpass.getpass()
                if password:
                    password_again = getpass.getpass('Password again:')
                    if password == password_again:
                        user = User.new(
                            name=name,
                            email=email,
                        )
                        if user:
                            User.change_password(
                                id_=user.id,
                                password=password,
                            )
                            print 'Thanks.'
                            need_info = False
                    else:
                        print 'passwords did not match.'



def downgrade():
    op.drop_table('user_teams')
    op.drop_table('teams')
    op.drop_table('users')