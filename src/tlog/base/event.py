from user import User
from tlog import models
from tlog.decorators import new_session
from datetime import datetime
from sqlalchemy import desc

class Log_group_event(object):
    
    def __init__(self, id_, log_group_id, user, message, time_):
        '''
        :param id_: int
        :param log_group_id: int
        :param user: tlog.base.user.User
        :param message: str
        :param time_: Datetime
        '''
        self.id = id_
        self.log_group_id = log_group_id
        self.user = user
        self.message = message
        self.time = time_

    @classmethod
    def new(cls, log_group_id, user_id, message):
        '''
        Creates a new event for a log group.

        :param log_group_id: int
        :param user_id: int
        :param message: str
        '''
        with new_session() as session:
            event = models.Log_group_event(
                log_group_id=log_group_id,
                user_id=user_id,
                message=message,
                time=datetime.utcnow(),
            )
            session.add(event)
            return True

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Log_group_event
        '''
        if not query:
            return None
        return cls(
            id_=query.Log_group_event.id,
            log_group_id=query.Log_group_event.log_group_id,
            user=User._format_from_query(query.User),
            message=query.Log_group_event.message,
            time_=query.Log_group_event.time,
        )

class Log_group_events(object):

    @classmethod
    def get(cls, log_group_id):
        '''
        Retrieves a list of log group events.

        :param log_group_id: int
        :returns: list of Log_group_event
        '''
        with new_session() as session:
            query = session.query(
                models.Log_group_event,
                models.User,
            ).filter(
                models.Log_group_event.log_group_id==log_group_id,
                models.User.id==models.Log_group_event.user_id,
            ).order_by(
                desc(models.Log_group_event.time)
            ).all()
            events = []
            for event in query:
                events.append(Log_group_event._format_from_query(event))
            return events