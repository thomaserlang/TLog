import logging
from tlog.constants import MINUTE_NORMALIZATION
from tlog.decorators import new_session
from sqlalchemy import func
from datetime import datetime, timedelta
from tlog.base.filter import Filter, Filters
from tlog import models
from tlog import utils
from tlog.base.notification import Filter_notification_last_sent
from tlog.receiver.notifier import Notifier

class Filter_warning(object):

    def __init__(self, filter_, from_date, normalized_count, threshold):
        '''
        :param filter_id: tlog.base.filter.Filter
        :param from_date: datetime
        :param normalized_count: int
        :param threshold: int
        :param min_logs: int
        '''
        self.filter = filter_
        self.from_date = from_date
        self.normalized_count = normalized_count
        self.threshold = threshold

    @classmethod
    def get_filters_to_check(cls):
        '''
        Retrieves a list of filters that has been active in the latest interval.
        These filters should be check for early warning.

        :returns: list of Filter_warning
        '''
        now = datetime.utcnow()
        from_date = now - timedelta(minutes=MINUTE_NORMALIZATION)
        with new_session() as session:
            query = session.query(
                models.Times_seen_by_minute,
                models.Filter,   
                func.sum(models.Times_seen_by_minute.times_seen).label('times_seen'),   
            ).filter(
                models.Times_seen_by_minute.time >= from_date,
                models.Filter.id == models.Times_seen_by_minute.filter_id,
            ).group_by(
                models.Times_seen_by_minute.filter_id,
            ).all()
            check = []
            for data in query:
                filter_ = Filter._format_from_query(data.Filter)             
                if filter_.data.get('rate_warning', {}).get('enabled', False):
                    if data.times_seen == 0:
                        continue
                    minutes = (now - data.Times_seen_by_minute.time).seconds / 60
                    if minutes == 0:
                        continue
                    normalized_count = int(data.times_seen / ((now - data.Times_seen_by_minute.time).seconds / 60))
                    min_logs = filter_.data['rate_warning'].get('min_logs', 100)
                    if normalized_count >= min_logs:
                        check.append(
                            cls(
                                filter_=filter_,
                                from_date=from_date,
                                normalized_count=normalized_count,
                                threshold=filter_.data['rate_warning'].get('threshold', 500),
                            )
                        )
            return check

    @classmethod
    def check_filter_warning(cls, filter_warning):
        '''
        Sends a warning notification if `filter_warning` has increased its threshold for received log messages.
        Returns True if a warning has been send.

        :param filter_warning: Filter_warning
        :returns: boolean
        '''

        intervals = 8 # 2 hours if `MINUTE_NORMALIZATION` is 15 minutes.

        min_date = filter_warning.from_date - timedelta(minutes=(intervals * MINUTE_NORMALIZATION))
        with new_session() as session:
            query = session.query(
                models.Times_seen_by_minute,
                func.sum(models.Times_seen_by_minute.times_seen).label('times_seen'),   
            ).filter(
                models.Times_seen_by_minute.filter_id == filter_warning.filter.id,
                models.Times_seen_by_minute.time >= min_date,
                models.Times_seen_by_minute.time <= filter_warning.from_date,
            ).group_by(
                models.Times_seen_by_minute.time,
                models.Times_seen_by_minute.filter_id,
            ).all()
            
            data = []
            for q in query:
                data.append(int(q.times_seen))
        if len(data) < intervals:
            logging.info('Not enough data points ({})'.format(len(data)))
            return False

        mean = utils.mean(data)
        mad = utils.mad(data)
        # this should give a better average number 
        # which takes deviation between the numbers into account.  
        normalized_prev_count = (mean + mad * 2) / MINUTE_NORMALIZATION

        # 100% would mean that the `normalized_count` is equal to the `normalized_prev_count` calculated number. 
        increase = filter_warning.normalized_count / normalized_prev_count * 100 
        logging.info('Calculated increase from {} to {} (+{}%)'.format(
            normalized_prev_count, 
            filter_warning.normalized_count, 
            increase
        ))
        if increase > filter_warning.threshold:
            if Filter_notification_last_sent.check(filter_id=filter_warning.filter.id): 
                logging.info('Sending notification to:')         
                Filter_notification_last_sent.update(filter_id=filter_warning.filter.id)
                Notifier.send(
                    message=u'Early warning. Rate of log messages per minute increased from {} to {} (+{}%) for filter {}.'.format(
                        normalized_prev_count, 
                        filter_warning.normalized_count, 
                        increase, 
                        filter_warning.filter.name,
                    ), 
                    filters=[
                        filter_warning.filter,
                    ],
                    force_send=True,
                )
            else:
                logging.info('Notification sent within the latest 30 minutes')
            return True
        else:
            logging.info('Increase was not higher than threshold. ({})'.format(increase))
        return False

    @classmethod
    def check_filter_warnings(cls, filter_warnings):
        '''
        Checks if theres is any warnings that should be sent out.

        :param filter_warnings: list of Filter_warning
        '''
        for filter_warning in filter_warnings:
            cls.check_filter_warning(
                filter_warning=filter_warning,
            )

class Filter_inactivity(object):

    @classmethod
    def check(cls):
        f = Filters.get()
        filters = {}
        filter_ids = []
        for filter_ in f:
            if 'inactivity' in filter_.data:
                if filter_.data['inactivity'].get('enabled', False):
                    filters[filter_.id] = filter_
                    filter_ids.append(filter_.id)
        if not filters:
            return False
        with new_session() as session:
            times_seen = session.query(
                models.Times_seen_by_minute.filter_id,
                func.max(models.Times_seen_by_minute.time).label('time'),
            ).filter(
                models.Times_seen_by_minute.filter_id.in_(filter_ids),
            ).group_by(
                models.Times_seen_by_minute.filter_id,
            ).all()
            inactive_filters = []
            now = datetime.utcnow()
            for seen in times_seen:
                max_inactive_minutes = filters[seen.filter_id].data['inactivity'].get('minutes')
                if max_inactive_minutes < MINUTE_NORMALIZATION:
                    max_inactive_minutes = MINUTE_NORMALIZATION
                if ((now - seen.time).seconds / 60) > max_inactive_minutes:
                    inactive_filters.append(filters[seen.filter_id])
                filters.pop(seen.filter_id, None)
            for filter_ in filters:
                inactivity_filters.append(filters[filter_])

            logging.info('{} inactive filters'.format(len(inactive_filters)))
            if not inactive_filters:
                return False

            for filter_ in inactive_filters:
                if Filter_notification_last_sent.check(filter_id=filter_.id):     
                    Filter_notification_last_sent.update(filter_id=filter_.id)
                    Notifier.send(
                        message=u'Early warning. Filter: {} has been marked as inactive.'.format(
                            filter_.name,
                        ), 
                        filters=[
                            filter_,
                        ],
                        force_send=True,
                    )
            return True