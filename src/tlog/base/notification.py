import logging
from tlog.decorators import new_session
from tlog import models
from tlog import constants
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

class Filter_notification_last_sent(object):

    @classmethod
    def update(cls, filter_id):
        '''
        Updates a filter_id's last sent time.

        :param filter_id: int
        :return boolean
        '''
        with new_session() as session:
            last_sent = models.Filter_notification_last_sent(
                filter_id=filter_id,
                last_sent=datetime.utcnow(),
            )
            try:
                session.merge(last_sent)
                session.commit()
                return True
            except IntegrityError as e:
                # Try again if there was a duplicate key.
                logging.exception('Filter notification duplicate key, trying again.')
                return cls.update(filter_id)

    @classmethod
    def check(cls, filter_id, minutes=constants.FILTER_NOTIFICATION_MINUTE_LIMIT):
        '''
        Returns true if there hasnt been sent any notifications to `filter_id` in the last `minutes`.

        :param filter_id: int
        :param minutes: int
        :returns: boolean
        '''
        with new_session() as session:
            query = session.query(
                models.Filter_notification_last_sent,
            ).filter(
                models.Filter_notification_last_sent.filter_id == filter_id,
                models.Filter_notification_last_sent.last_sent > (datetime.utcnow() - timedelta(minutes=minutes)),
            ).first()
            if query:
                return False
        return True

class Log_group_notification_last_sent(object):

    @classmethod
    def update(cls, log_group_id):
        '''
        Updates a log_group_id's last sent time.

        :param log_group_id: int
        :return boolean
        '''
        with new_session() as session:
            last_sent = models.Log_group_notification_last_sent(
                log_group_id=log_group_id,
                last_sent=datetime.utcnow(),
            )
            try:
                session.merge(last_sent)
                session.commit()
                return True
            except IntegrityError as e:
                # Try again if there was a duplicate key.
                logging.exception('Log group notification duplicate key, trying again.')
                return cls.update(log_group_id)

    @classmethod
    def check(cls, log_group_id, minutes=constants.LOG_GROUP_NOTIFICATION_MINUTE_LIMIT):
        '''
        Returns true if there hasnt been sent any notifications to `log_group_id` in the last `minutes`.

        :param log_group_id: int
        :param minutes: int
        :returns: boolean
        '''
        with new_session() as session:
            query = session.query(
                models.Log_group_notification_last_sent,
            ).filter(
                models.Log_group_notification_last_sent.log_group_id == log_group_id,
                models.Log_group_notification_last_sent.last_sent > (datetime.utcnow() - timedelta(minutes=minutes)),
            ).first()
            if query:
                return False
            return True
