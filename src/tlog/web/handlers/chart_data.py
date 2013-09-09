import base
import time
import logging
from tlog.decorators import new_session
from tlog import models
from datetime import datetime, timedelta
from sqlalchemy import func
from tlog.constants import MINUTE_NORMALIZATION
from tlog.utils import normalize_datetime
from calendar import timegm
from tlog.base.filter import Filters_user
from tornado.web import authenticated
from tlog import constants

class Times_seen_handler(base.API_handler):

    def prefill_data(self, from_, to):
        '''
        Prefills a list of dict.

        :param from_: datetime
        :param to: datetime
        :returns: list of dict
        '''
        from_ = int(
            timegm(
                normalize_datetime(from_).timetuple()
            )
        )
        to = int(
            timegm(
                normalize_datetime(to).timetuple()
            )
        )
        data = []
        for i in xrange(1, ((to - from_) / 60) / MINUTE_NORMALIZATION + 1):
            timestamp = int(from_ + ((i * MINUTE_NORMALIZATION) * 60))
            data.append({                    
                'x': timestamp,
                'y': 0,
            })
        return data

class Times_seen_log_group_handler(Times_seen_handler):

    @authenticated
    def get(self, log_group_id):
        from_ = datetime.utcnow() - timedelta(days=int(self.get_argument('days', 1)))
        with new_session() as session:
            query = session.query(
                func.min(models.Times_seen_by_minute.time).label('time'),
                func.max(models.Times_seen_by_minute.times_seen).label('times_seen'), 
            ).filter(
                models.Times_seen_by_minute.log_group_id == log_group_id,
                models.Times_seen_by_minute.time >= from_,
            ).group_by(
                models.Times_seen_by_minute.time,
                models.Times_seen_by_minute.log_group_id,
            ).all()  
            data = self.prefill_data(from_, datetime.utcnow())          
            for d in query:
                timestamp = int(timegm(d.time.timetuple()))
                for a in data:
                    if a['x'] == timestamp:
                        a['y'] = int(d.times_seen)
            self.write_object([
                {
                    "color": "#cae2f7",
                    "name": "Times seen",
                    "data": data,
                }
            ])

class Times_seen_filter_handler(Times_seen_handler):

    @authenticated
    def get(self, filter_id):
        from_ = datetime.utcnow() - timedelta(days=int(self.get_argument('days', 1)))
        with new_session() as session:
            query = session.query(
                func.min(models.Times_seen_by_minute.time).label('time'),
                func.sum(models.Times_seen_by_minute.times_seen).label('times_seen'), 
            ).filter(
                models.Times_seen_by_minute.filter_id == filter_id,
                models.Times_seen_by_minute.time >= from_,
            ).group_by(
                models.Times_seen_by_minute.time,
                models.Times_seen_by_minute.filter_id,
            ).all()  
            data = self.prefill_data(from_, datetime.utcnow())          
            for d in query:
                timestamp = int(timegm(d.time.timetuple()))
                for a in data:
                    if a['x'] == timestamp:
                        a['y'] = int(d.times_seen)
            self.write_object([
                {
                    "color": "#cae2f7",
                    "name": "Times seen",
                    "data": data,
                }
            ])

class Times_seen_user_filters_handler(Times_seen_handler):

    @authenticated
    def get(self):
        from_ = datetime.utcnow() - timedelta(days=int(self.get_argument('days', 1)))
        filters = Filters_user.get(user_id=self.current_user.id)
        now = datetime.utcnow() 
        filter_ids = []
        data = {}
        for i, filter_ in enumerate(filters):
            filter_ids.append(filter_.id)
            data.setdefault(filter_.id, {})
            data[filter_.id]['data'] = self.prefill_data(from_, now)
            data[filter_.id]['name'] = filter_.name
            data[filter_.id]['color'] = constants.COLORS[i]
        if not filters:
            data[0] = {}
            data[0]['data'] = self.prefill_data(from_, now)
            data[0]['name'] = ''
            data[0]['color'] = constants.COLORS[0]
        with new_session() as session:
            query = session.query(
                func.min(models.Times_seen_by_minute.time).label('time'),
                func.sum(models.Times_seen_by_minute.times_seen).label('times_seen'), 
                func.min(models.Times_seen_by_minute.filter_id).label('filter_id'),
            ).filter(
                models.Times_seen_by_minute.filter_id.in_(filter_ids),
                models.Times_seen_by_minute.time >= from_,
                models.Filter.id == models.Times_seen_by_minute.filter_id,
            ).group_by(
                models.Times_seen_by_minute.time,
                models.Times_seen_by_minute.filter_id,
            ).all()                  
            for d in query:
                timestamp = int(timegm(d.time.timetuple()))
                for a in data[d.filter_id]['data']:
                    if a['x'] == timestamp:
                        a['y'] = int(d.times_seen)
            data_list = []
            for key in data:
                data_list.append(data[key])
            self.write_object(data_list)
