import time
import math
import logging
from tlog.decorators import new_session
from tlog import models
from tlog import utils
from tlog.base.filter import Filter
from datetime import datetime
from sqlalchemy import func, or_, and_
from sqlalchemy.exc import IntegrityError

class Log_group(object):

    def __init__(self, id_, message, message_hash, first_seen, last_seen, last_log_id, times_seen, level, score, status, reopened):
        '''
        :param id_: int
        :param message: str
        :param message_hash str
        :param first_seen: datetime
        :param lst_seen: datetime
        :param last_log_id: int
        :param level: int
            Uses Syslog severity levels. See http://en.wikipedia.org/wiki/Syslog#Severity_levels
        :param score: int
            math.log({group.times_seen}*(8-{level}) + time.time())
        :param status: int
            See tlog.constants.STATUS_LEVELS
        :param reopened: datetime
        '''
        self.id = id_
        self.message = message
        self.message_hash = message_hash
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.last_log_id = last_log_id
        self.times_seen = times_seen
        self.level = level
        self.score = score
        self.status = status
        self.reopened = reopened

    @classmethod
    def get(cls, message_hash):
        '''

        :param message_hash: str
        :returns: Log_group
        '''
        with new_session() as session:
            group = session.query(
                models.Log_group,
            ).filter(
                models.Log_group.message_hash==message_hash,
            ).first()
            return cls._format_from_query(group)

    @classmethod
    def get_by_id(cls, id_):
        '''

        :param id_: int
        :returns: Log_group
        '''
        with new_session() as session:
            group = session.query(
                models.Log_group,
            ).filter(
                models.Log_group.id==id_,
            ).first()
            return cls._format_from_query(group)

    @classmethod
    def delete(cls, id_):
        '''
        Deletes the log group and all its relations.

        :param id_: int
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.Log_group,
            ).filter(
                models.Log_group.id==id_,
            ).delete()
            session.commit()
            return True

    @classmethod
    def add(cls, store):
        '''
        Tries to group the `store` object with other stored objects, that has the same message_hash.

        :param store: tlog.receiver.store.Store
        :returns: Log_group
        '''
        with new_session() as session:
            query = session.query(
                models.Log_group,
            ).filter(
                models.Log_group.message_hash==store.message_hash,
            ).update({
                'level': store.level,
            })
            if not query:
                group = models.Log_group(
                    message = store.data.get('message', ''),
                    message_hash = store.message_hash,
                    level = store.level,
                )
                try:
                    session.add(group)
                    session.commit()
                    return cls._format_from_query(group)
                except IntegrityError as e:
                    # Try again if there was a duplicate key.
                    logging.error(unicode(e))
                    return cls.add(store)
            else:
                return cls.get(
                    message_hash=store.message_hash,
                )
                
    @classmethod
    def inc_seen(cls, log_group):
        '''
        Use this funtion to inc times_seen and change last_seen to now.

        :param log_group: Log_group
        :returns: boolean
        '''
        with new_session() as session:
            cls._inc_seen(session, log_group)
            return True
    @classmethod
    def _inc_seen(cls, session, log_group): 
        session.query(
            models.Log_group,
        ).filter(
            models.Log_group.id==log_group.id,
        ).update({
            'last_seen': datetime.utcnow(),     
            'times_seen': models.Log_group.times_seen + 1,           
            'score': math.log(log_group.times_seen + 1) * 600 + time.time(),                
        })

    @classmethod
    def update_status(cls, id_, status, reopened=None):
        '''
        Updates a log groups status.
        If the status went from 1 to 0, it would be smart to set the time 
        for when it reopened.

        :param id_: int
        :param status: int
            See tlog.constants.STATUS_LEVELS
        :param reopened: datetime
        :returns: boolean
        '''
        with new_session() as session:
            session.query(
                models.Log_group,
            ).filter(
                models.Log_group.id==id_,
            ).update({
                'status': status,
                'reopened': reopened,
            })
            return True

    @classmethod
    def update_last_log_id(cls, id_, last_log_id):
        '''
        Updates the last_log_id field.
        Should be called after a new message has been written to the logs table.

        :param id_: int
        :param last_log_id: int
        :returns: boolean
        '''
        with new_session() as session:
            cls._update_last_log_id(session, id_, last_log_id)
            return True
    @classmethod
    def _update_last_log_id(cls, session, id_, last_log_id):
        session.query(
            models.Log_group,
        ).filter(
            models.Log_group.id==id_,
        ).update({
            'last_log_id': last_log_id,
        })

    @classmethod
    def _format_from_query(cls, query):
        '''
        :param query: query
        :returns: Log_group
        '''
        if not query:
            return None
        return cls(
            id_=query.id,
            message=query.message,
            message_hash=query.message_hash,
            first_seen=query.first_seen,
            last_seen=query.last_seen,
            last_log_id=query.last_log_id,
            times_seen=query.times_seen,
            level=query.level,
            score=query.score,
            status=query.status,
            reopened=query.reopened,
        )

class Log_groups(object):

    @classmethod
    def get(cls, filters, strict_version=False, extra_filter=None, order_by=None, limit=25, offset=0):
        '''
        Retrieves a list of `Log_group` by filters.

        :param filters: list of Filter
        :param strict_version: boolean
            If true the id and version from `filters` has to match in the relation.
        :param extra_filter: list of models fields to match (SQLALchemy filter)
            extra_filter=[models.Log_group.id==1]
        :param: order_by: list of models fields (SQLALchemy order_by)
            order_by=[models.Log_group.id, models.Log_group.score]
        :param limit: int
        :param offset: int
            Page 2 would be limit*2
        :returns: list of tlog.base.log_group.Log_group
        '''
        if not filters:
            return []
        with new_session() as session:
            query = session.query(
                models.Log_group,
            )
            if strict_version:
                f = []
                for filter_ in filters:                    
                    f.append(and_(models.Filter_log_group.filter_id == filter_.id, models.Filter_log_group.filter_version == filter_.version))
                query = query.filter(
                    or_(*f)
                )
            else:
                ids = []
                for filter_ in filters:
                    ids.append(filter_.id)
                query = query.filter(
                    models.Filter_log_group.filter_id.in_(ids)
                )
            query = query.filter(
                models.Log_group.id == models.Filter_log_group.log_group_id,
            )
            if extra_filter:
                query = query.filter(*extra_filter)
            if order_by:
                query = query.order_by(*order_by)
            query = query.group_by(
                models.Log_group.id,
            )
            query = query.limit(limit).offset(offset)
            query.all()
            groups = []
            for group in query:
                groups.append(Log_group._format_from_query(group))
            return groups

class Log_group_filters(object):

    @classmethod
    def add(cls, filters, log_group_id):
        '''
        Creates a relation between a log_group and on or more filters.

        :param filter_: list of Filter
        :param log_group_id: int
        :returns: boolean
        '''
        with new_session() as session:
            for filter_ in filters:
                f = models.Filter_log_group(
                    filter_id=filter_.id,
                    filter_version=filter_.version,
                    log_group_id=log_group_id,
                )
                session.merge(f)
            try:
                session.commit()
                return True
            except IntegrityError as e:
                # Try again if there was a duplicate key.
                logging.error(unicode(e))
                return cls.add(filters, log_group_id)

    @classmethod
    def get(cls, log_group_id):
        '''
        Returns a list of filters by `log_group_id`.

        :param log_group_id: int
        :returns: list of Filter
        '''
        with new_session() as session:
            query = session.query(
                models.Filter,
            ).filter(
                models.Filter_log_group.log_group_id == log_group_id,
                models.Filter.id==models.Filter_log_group.filter_id,
            ).all()
            filters = []
            for filter_ in query:
                filters.append(Filter._format_from_query(filter_))
            return filters