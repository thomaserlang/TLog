import json
from tlog import models
from tlog.decorators import new_session
from tlog.base.team import Team
from sqlalchemy.exc import IntegrityError

'''
#Filter data
Each filter has a variable called `data`.
In `data`, all the settings and which log messages to match or not match are stored.

Example:
    
    {
        "match": {
            "data": {
                "severity": [
                    "[0-9]+"
                ]
            }
        },
        "notmatch": {
            "hostname": [
                "te-pc"
            ]
        },
        "store": true,
        "notify": true
    }

The filter above would match a log message with any severity level and not coming from te-pc.

## match and notmatch
`match` and `notmatch` defines what has to match and/or not match.
Each field specified in `match` and `notmatch` has to be accompanied by a value of a list of regular expressions.

### hostname
`hostname` is the name of the sender.

Example:

    "hostname": [
        "^web-.*$"
    ]

### level
`level` is the same as a severity level in the Syslog protocol (http://en.wikipedia.org/wiki/Syslog#Severity_levels).

Example:

    "level": [
        "[0-3]+"
    ]

### data
`data` holds all other data like the message or priority level received from a syslog message.
Any parameters sent with the log message will be available for filtering in this field too. 

Example: 

    "data": {
        "severity": [
            "[0-3]+"
        ],
        "facility": [
            "[5-8]+"
        ],
        "message": [
            ".*Warning.*"
        ]
    }

## notify
`notify` excepts a boolean value. 
If true, a log message matching the filter would trigger a notification.

    OBS! Each received log is group by its message hash.
    A notification will only be sent if there hasn't been sent on for the log group in the last 30 minutes.

## save
`save ` excepts a boolean value.
If true the received log message will be saved.

## rate_warning
`rate_warning` is a early warning system.
It checks every filter for how many logs has been received in the last 2 hours and compares that to the latest minute.
If the increase in the latest minute is higher than the specified threshold and the minimum number of logs has been received, then a warning will be sent.

Example:

    "rate_warning": {
        "enabled": true,
        "threshold": 500,
        "min_logs": 100
    }

### enable
`enable ` excepts a boolean value.
If true a warning could be sent.

### threshold
`threshold` excepts a integer.
Specify any number in percentage.
500 would mean that the increased rate per minute would have to higher than 500%, to trigger the warning.

### min_logs
`min_logs` excepts a integer.
Set a minimum number of logs received in a minute to trigger the warning.

'''

class Filter(object):
    
    def __init__(self, id_, version, name, data):
        '''
        :param id_: int
        :param version: int
        :param name: str
        :param data: dict
        '''
        self.id = id_
        self.version = version
        self.name = name
        self.data = data

    @classmethod
    def new(cls, name, data):
        '''
        Creates a new filter and adds it to the versioning table.

        :param name: str
        :param data: dict
        :returns: Filter
        '''
        if not isinstance(data, dict):
            raise Exception('data must be a dict')
        with new_session() as session:
            filter_ = models.Filter(
                name=name, 
                data=json.dumps(data),
            )
            session.add(filter_)
            session.commit()
            filter_ = cls._format_from_query(filter_)
            Filter_version.new(filter_)
            return filter_

    @classmethod
    def update(cls, id_, name, data):
        '''
        Updates the filter and creates a new version in the versioning table.

        :param id_: int
        :param name: str
        :param data: dict
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.Filter,
            ).filter(
                models.Filter.id==id_,
            ).update({
                'name': name,
                'data': json.dumps(data),
                'version': models.Filter.version + 1,
            })
            session.commit()
            Filter_version.new(filter_=cls.get(id_=id_))
            return True

    @classmethod
    def get(cls, id_):
        '''
        Retrieves a filter by it's id.

        :param id_: int
        :returns: Filter
        '''
        with new_session() as session:
            query = session.query(
                models.Filter,
            ).filter(
                models.Filter.id==id_,
            ).first()
            return cls._format_from_query(query)

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Filter
        '''
        if not query:
            return None
        return cls(
            id_=query.id,
            version=query.version,
            name=query.name,
            data=json.loads(query.data),
        )

class Filters(object):

    @classmethod
    def get(cls):
        '''
        Retrieves all filters.

        :returns: list of Filter
        '''
        with new_session() as session:
            query = session.query(
                models.Filter,
            ).all()
            filters = []
            for filter_ in query:
                filters.append(Filter._format_from_query(filter_))
            return filters

class Filter_version(object):

    def __init__(self, filter_id, version, data):
        '''

        :param filter_id: int
        :param version: int
        :param data: dict
        '''
        self.filter_id = filter_id
        self.version = version
        self.data = data

    @classmethod
    def new(cls, filter_):
        '''
        Creates `filter_` in the table filter_versions.

        :param filter_: Filter
        :returns: boolean
        '''
        with new_session() as session:
            filter_version = models.Filter_version(
                filter_id=filter_.id,
                version=filter_.version,
                data=json.dumps(filter_.data),
            )
            session.add(filter_version)
            session.commit()
            return True

    @classmethod
    def get(cls, filter_id, version):
        '''
        Retrieves a filter from the versioning table.

        :param filter_id: int
        :param version: int
        :returns: Filter_version
        '''
        with new_session() as session:
            query = session.query(
                models.Filter_version,
            ).filter(
                models.Filter_version.filter_id==filter_id,
                models.Filter_version.version==version,
            ).first()
            return cls._format_from_query(query)

    @classmethod
    def _format_from_query(cls, query):
        '''

        :param query: query
        :returns: Filter_version
        '''
        if not query:
            return None
        return cls(
            filter_id=query.filter_id,
            version=query.version,
            data=json.loads(query.data),
        )

class Filter_team(object):
    '''
    Filter - Team: relation.
    '''

    @classmethod
    def new(cls, filter_id, team_id):
        '''
        Creates a new filter team relation.

        :param filter_id: int
        :param team_id: int
        :returns: boolean
        '''
        with new_session() as session:
            ft = models.Filter_team(
                filter_id=filter_id,
                team_id=team_id,
            )
            session.merge(ft)
            session.commit()
            return True

    @classmethod
    def delete(cls, filter_id, team_id):
        '''
        Deletes a filter team relation.

        :param filter_id: int
        :param team_id: int
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.Filter_team,
            ).filter(
                models.Filter_team.filter_id==filter_id,
                models.Filter_team.team_id==team_id,
            ).delete()
            session.commit()
            return True

    @classmethod
    def get_teams_by_filter_id(cls, filter_id):
        '''
        Retrieves a list of teams from a filter_id.

        :param filter_id: int
        :returns: list of tlog.base.team.Team
        '''
        with new_session() as session:
            query = session.query(
                models.Filter_team,
                models.Team,
            ).filter(
                models.Filter_team.filter_id==filter_id,
                models.Team.id==models.Filter_team.team_id,
            ).all()
            teams = []
            for team in query:
                teams.append(Team._format_from_query(team.Team))
            return teams

class Filters_user(object):

    @classmethod
    def get(cls, user_id):
        '''
        Retreives a list of filters by a `user_id`.

        :param user_id: int
        :returns: list of Filter
        '''
        with new_session() as session:
            query = session.query(
                models.Filter,
            ).filter(
                models.User_team.user_id == user_id,
                models.Filter_team.team_id == models.User_team.team_id,
                models.Filter.id == models.Filter_team.filter_id,
            ).group_by(
                models.Filter.id,
            ).order_by(
                models.Filter.name,
            ).all()
            filters = []
            for filter_ in query:
                filters.append(Filter._format_from_query(filter_))
            return filters
