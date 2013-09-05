from tlog.decorators import new_session
from tlog import models
from sqlalchemy import asc

class Team_exception_duplicate_name(Exception):
    pass

class Team(object):

    def __init__(self, id_, name):
        '''
        :param id_: int
        :param name: str
        '''
        self.id = id_
        self.name = name

    @classmethod
    def new(cls, name):
        '''
        Creates a new.

        :param name: str
        :returns: Team
        '''
        team = cls.get_by_name(name=name)
        if team:
            raise Team_exception_duplicate_name('The team name is already in use.')
        with new_session() as session:
            team = models.Team(
                name=name,
            )
            session.add(team)
            session.commit()
            return cls._format_from_query(team)

    @classmethod
    def update(cls, id_, name):
        '''
        :param id_: int
        :param name: str
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.Team,
            ).filter(
                models.Team.id==id_
            ).update({
                'name': name,
            })
            session.commit()
            return True

    @classmethod
    def get(cls, id_):
        '''
        :param id_: int
        :returns: Team
        '''
        with new_session() as session:
            team = session.query(
                models.Team,
            ).filter(
                models.Team.id==id_,
            ).first()
            return cls._format_from_query(team)

    @classmethod
    def get_by_name(cls, name):
        '''
        :param name: str
        :returns: Team
        '''
        with new_session() as session:
            team = session.query(
                models.Team,
            ).filter(
                models.Team.name==name,
            ).first()
            return cls._format_from_query(team)

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Team
        '''
        if not query:
            return None
        return cls(
            id_=query.id,
            name=query.name,
        )

class Teams(object):

    @classmethod
    def get(cls):
        '''
        Retrieves all teams.

        :returns: list of Team
        '''
        with new_session() as session:
            query = session.query(
                models.Team,
            ).order_by(
                asc(models.Team.name),
            ).all()
            teams = []
            for team in query:
                teams.append(Team._format_from_query(team))
            return teams