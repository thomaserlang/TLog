import json
import logging
from tlog.decorators import new_session
from tlog import models
from sqlalchemy import desc, asc

class Log(object):

    def __init__(self, id_, external_id, received, message_hash, data, hostname, level, log_group_id):
        '''
        :param id_: int
        :param external_id: str
        :param received: datetime
        :param message_hash: str
        :param data: dict
            Example:
                {
                    "message": "Some message",
                    "priority": 123
                }
        :param hostname: str
        :param level: int
        :param log_group_id
        '''
        self.id = id_
        self.external_id = external_id
        self.received = received
        self.message_hash = message_hash
        self.data = data
        self.hostname = hostname
        self.level = level
        self.log_group_id = log_group_id

    @classmethod
    def get(cls, id_):
        '''
        :param id_: int
        :returns: Log
        '''
        with new_session() as session:
            query = session.query(
                models.Log,
            ).filter(
                models.Log.id == id_,
            ).first()
            return cls._format_from_query(query)

    @classmethod
    def get_prev(cls, id_, log_group_id):
        '''
        Returns a previous log in the same log group.

        :param id_: int
        :returns: Log
        '''
        with new_session() as session:
            query = session.query(
                models.Log,
            ).filter(
                models.Log.log_group_id==log_group_id,
                models.Log.id < id_,
            ).order_by(
                desc(models.Log.id),
            ).first()
            return cls._format_from_query(query)

    @classmethod
    def get_next(cls, id_, log_group_id):
        '''
        Returns a next log in the same log group.

        :param id_: int
        :returns: Log
        '''
        with new_session() as session:
            query = session.query(
                models.Log,
            ).filter(
                models.Log.log_group_id==log_group_id,
                models.Log.id > id_,
            ).order_by(
                asc(models.Log.id),
            ).first()
            return cls._format_from_query(query)

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Log
        '''
        if not query:
            return None
        return cls(
            id_=query.id,
            external_id=query.external_id,
            received=query.received,
            message_hash=query.message_hash,
            data=json.loads(query.data),
            hostname=query.hostname,
            level=query.level,
            log_group_id=query.log_group_id,
        )

