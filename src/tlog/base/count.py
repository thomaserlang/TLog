import logging
from tlog import models
from tlog.decorators import new_session
from tlog.constants import MINUTE_NORMALIZATION
from tlog import utils
from datetime import datetime, timedelta
from sqlalchemy import func

class Times_seen_by_minute(object):

    def __init__(self, time, log_group_id, filter_id, times_seen):
        '''
        :param time: datetime
        :param log_group_id: int
        :param times_seen: int
        '''
        self.time = time
        self.log_group_id = log_group_id
        self.filter_id = filter_id
        self.times_seen = times_seen

    @classmethod
    def update(cls, log_group_id, filter_id, when=None, inc=1):
        '''
        Increments times_seen for the latest minute by log_group_id and filter_id.

        :param log_group_id: int
        :param filter_id: int
        :param when: datetime - default None
            If none a normalized current date and time will be used.
        :param inc: int - default 1
            The number of times `times_seen` should be incremented.
        :returns: boolean
        '''
        with new_session() as session:
            cls._update(session, log_group_id, filter_id, when, inc)
            return True
    @classmethod
    def _update(cls, session, log_group_id, filter_id, when=None, inc=1):
        if not when:
            when = utils.normalize_datetime(datetime.utcnow())
        query = session.query(
            models.Times_seen_by_minute,
        ).filter(
            models.Times_seen_by_minute.log_group_id==log_group_id,
            models.Times_seen_by_minute.filter_id==filter_id,
            models.Times_seen_by_minute.time==when,
        ).update({
            'times_seen': models.Times_seen_by_minute.times_seen + inc,
        })        
        if not query:
            query = models.Times_seen_by_minute(
                time=when,
                log_group_id=log_group_id,
                filter_id=filter_id,
                times_seen=inc,
            )
            session.add(query)

    @classmethod
    def get_by_log_group_id(cls, log_group_id):
        '''
        :param log_group_id: int
        :returns: list of Times_seen_by_minute
        '''
        with new_session() as session:
            query = session.query(
                models.Times_seen_by_minute,
            ).filter(
                models.Times_seen_by_minute.log_group_id==log_group_id
            ).all()
            minutes = []
            for minute in query:
                minutes.append(cls._format_from_query(minute))
            return minutes

    @classmethod
    def get_logs_per_minute(cls, filter_id):
        '''
        Returns logs received per minute for the latest interval.

        :param filter_id: int
        :returns: int
        '''
        now = datetime.utcnow()
        min_date = now - timedelta(minutes=MINUTE_NORMALIZATION)
        with new_session() as session:
            query = session.query(
                func.min(models.Times_seen_by_minute.time).label('time'),
                func.sum(models.Times_seen_by_minute.times_seen).label('times_seen'),   
            ).filter(
                models.Times_seen_by_minute.filter_id == filter_id,
                models.Times_seen_by_minute.time >= min_date,
            ).group_by(
                models.Times_seen_by_minute.filter_id,
            ).first()
            if not query:
                return 0
            if query.times_seen == 0:
                return 0
            seconds_normalized = (now - query.time).seconds / 60
            if seconds_normalized == 0:
                return 0
            return int(query.times_seen / seconds_normalized)

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Times_seen_by_minute
        '''
        if not query:
            return None
        return cls(
            time=query.time,
            log_group_id=query.log_group_id,
            filter_id=query.filter_id,
            times_seen=query.times_seen,
        )

class Server_count(object):

    def __init__(self, log_group_id, name, count):
        '''
        :param log_group_id: int
        :param name: str
        :param count: int
        '''
        self.log_group_id = log_group_id
        self.name = name
        self.count = count

    @classmethod
    def add(cls, log_group_id, name):
        '''
        Creates or updates a servers count for at log group.

        :param log_group_id: int
        :param name: str
        :returns: boolean
        '''
        with new_session() as session:
            cls._add(session, log_group_id, name)
            return True
    @classmethod
    def _add(cls, session, log_group_id, name):
        server = models.Log_group_server(
            name=name,
            log_group_id=log_group_id,
            count=models.Log_group_server.count + 1,
        )
        session.merge(server)

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Server_count
        '''
        if not query:
            return None
        return cls(
            log_group_id=query.log_group_id,
            name=query.name,
            count=query.count,
        )

class Servers_count(object):

    @classmethod
    def get(cls, log_group_id):
        '''
        :param log_group_id: int
        :returns: list of Server_count
        '''
        with new_session() as session:
            query = session.query(
                models.Log_group_server,
            ).filter(
                models.Log_group_server.log_group_id==log_group_id,
            ).all()
            servers = []
            for server in query:
                servers.append(Server_count._format_from_query(server))
            return servers