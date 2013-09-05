import json
import bcrypt
from tlog.decorators import new_session
from tlog import models
from tlog.base.team import Team
from sqlalchemy import asc

class User_exception_duplicate_email(Exception):
    pass

class User(object):
    '''
    Base class for a user.
    '''

    def __init__(self, id_, name, email, notification_types):
        '''
        :param id_: int
        :param name: str
        :param email: str
        :param notification_types: dict            
            notification_types = {
                'send_email': {
                    'data': 'test2@example.com',
                    'enabled': True,
                }
            }
        '''
        self.id = id_
        self.name = name
        self.email = email
        self.notification_types = notification_types

    @classmethod
    def new(cls, name, email, notification_types={}):
        '''
        Create a user.

        :param name: str
        :param email: str
        :returns: User
        :raises: User_exception_duplicate_email
        '''
        user = cls.get_by_email(email=email)
        if user:
            raise User_exception_duplicate_email('The email address is already in use.')
        with new_session() as session:
            user = models.User(
                name=name,
                email=email,
                notification_types=json.dumps(notification_types),
            )
            session.add(user)
            session.commit()
            return cls._format_from_query(user)

    @classmethod
    def get(cls, id_):
        '''
        Retrieves the user by its id.

        :param id_: int
        :returns: User
        '''
        with new_session() as session:
            user = session.query(
                models.User,
            ).filter(
                models.User.id==id_,
            ).first()
            return cls._format_from_query(user)

    @classmethod
    def get_by_email(cls, email):
        '''
        Retrieves the user by its email address.

        :param email: str
        :returns: User
        '''
        with new_session() as session:
            user = session.query(
                models.User,
            ).filter(
                models.User.email==email,
            ).first()
            return cls._format_from_query(user)

    @classmethod
    def change_password(cls, id_, password, current_password=None):
        '''
        Changes a users password.

        Set `current_password` to verify the users current password, before changing it.

        :param id: int
        :param password: str
        :param current_password: str
        :returns: boolean
        '''

        with new_session() as session:
            if current_password:
                if not cls.verify_password(id_=id_, password=current_password):
                    return False
            session.query(
                models.User,
            ).filter(
                models.User.id==id_,
            ).update({
                'password': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(10)),
            })
            session.commit()
            return True

    @classmethod
    def verify_password(cls, id_, password):
        '''
        Verifies that `password` is in fact the users password.

        :param id_: int
        :param password: str
        :returns: boolean
        '''
        with new_session() as session:
            user = session.query(
                models.User,
            ).filter(
                models.User.id==id_,
            ).first()
            if bcrypt.hashpw(password.encode('utf-8'), user.password) == user.password:
                return True
            return False

    @classmethod
    def login(cls, email, password):
        user = cls.get_by_email(
            email=email,
        )
        if not user:
            return False
        if not cls.verify_password(id_=user.id, password=password):
            return False
        return user

    @classmethod
    def update_notification_types(cls, id_, notification_types):
        '''
        Updates a users notification_types.

        :param id_: int
        :param notification_types: dict            
            notification_types = {
                'send_email': {
                    'data': 'test2@example.com',
                    'enabled': True,
                }
            }
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.User,
            ).filter(
                models.User.id == id_,
            ).update({
                'notification_types': json.dumps(notification_types)
            })
            session.commit()
            return True

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: 
        :returns: User
        '''
        if not query:
            return None
        return cls(
            id_=query.id,
            name=query.name,
            email=query.email,
            notification_types=json.loads(query.notification_types),
        )

class Users(object):

    @classmethod
    def get(cls):
        '''
        Retrieves all users.

        :returns: list of User
        '''
        with new_session() as session:
            query = session.query(
                models.User,
            ).order_by(
                asc(models.User.name),
            ).all()
            users = []
            for user in query:
                users.append(User._format_from_query(user))
            return users

class User_team(object):

    @classmethod
    def new(cls, user_id, team_id):
        '''
        Creates a relation between a user and a team.

        :param user_id: int
        :param team_id: int
        :returns: boolean
        '''
        with new_session() as session:
            ut = models.User_team(
                user_id=user_id,
                team_id=team_id,
            )
            session.merge(ut)
            session.commit()
            return True

    @classmethod
    def delete(cls, user_id, team_id):
        '''
        Deletes the relation between a user and a team.

        :param user_id: int
        :param team_id: int
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.User_team,
            ).filter(
                models.User_team.user_id==user_id,
                models.User_team.team_id==team_id,
            ).delete()
            session.commit()
            return True

class User_teams(object):

    @classmethod
    def get(cls, user_id):
        '''
        Retrieves a list of teams a given users is a member of.

        :param user_id: int
        :returns: list of tlog.base.team.Team
        '''
        with new_session() as session:
            query = session.query(
                models.User_team,
                models.Team,
            ).filter(
                models.User_team.user_id==user_id,
                models.Team.id==models.User_team.team_id,
            ).all()
            teams = []
            for team in query:
                teams.append(Team._format_from_query(team.Team))
            return teams

class Users_team(object):

    @classmethod
    def get(cls, team_id):
        '''
        Retrieves a members list for team_id.

        :param team_id: int
        :returns: list of User
        '''
        with new_session() as session:
            query = session.query(
                models.User_team,
                models.User,
            ).filter(
                models.User_team.team_id==team_id,
                models.User.id==models.User_team.user_id,
            ).all()
            users = []
            for user in query:
                users.append(User._format_from_query(user.User))
            return users

    @classmethod
    def get_by_team_list(cls, teams):
        '''
        Returns a grouped list of users that are members.

        :param teams: list of tlog.base.team.Team
        :returns: list of User
        '''
        if not teams:
            return []
        team_ids = []
        for team in teams:
            team_ids.append(team.id)
        with new_session() as session:
            query = session.query(
                models.User_team,
                models.User,
            ).filter(
                models.User_team.team_id.in_(team_ids),
                models.User.id==models.User_team.user_id,
            ).group_by(
                models.User.id,
            ).all()
            users = []
            for user in query:
                users.append(User._format_from_query(user.User))
            return users