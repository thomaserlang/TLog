# coding=UTF-8
import hashlib
import logging
from datetime import datetime
from tlog.utils import json_dumps
from tlog.receiver.parse import Parse
from tlog.receiver.notifier import Notifier
from tlog.decorators import new_session
from tlog.config import Config
from tlog.base.event import Log_group_event
from tlog import constants
from tlog.base.log_group import Log_group, Log_group_filters
from tlog.base.count import Times_seen_by_minute, Server_count
from tlog.base.notification import Log_group_notification_last_sent
from tlog import models
from uuid import uuid4
from pyelasticsearch import ElasticSearch
from sqlalchemy.exc import IntegrityError

class Store(object):
    '''
    Stores, groups and checks for rate limits for log messages.

    Example:

        store = Store(tlog.receiver.parse.Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'))
        store.save()
        >> True

    '''

    es = ElasticSearch(Config.data['elasticsearch']['url'])

    def __init__(self, parsed, matched_filters=[]):
        '''
        :param parsed: tlog.receiver.parse.parsed.Parsed
            A parsed log message.
        :param matched_filters: list of tlog.base.filter.Filter
        '''
        self.matched_filters = matched_filters
        self.valid = False
        if not parsed:
            return
        self.valid = True
        self.hostname = parsed.hostname
        self.level = parsed.level
        self.data = parsed.data
        self.external_id = unicode(uuid4()).replace('-', '')
        self.message_hash = hashlib.sha1(self.data.get('message', u'').encode('utf-8')).hexdigest()
        self.received = datetime.utcnow()
        self.log_group = None

    def count_limit(self, count):
        '''
        Returns a sample rate for the specified count.
        The sample rates must be specified in the config.

        :param count: int
        :returns: int
        '''
        if not Config.data['sample_rates']:
            return 1
        for amount, sample in Config.data['sample_rates']:
            if count <= amount:
                return sample
        return Config.data['max_sample_rate']
    
    def time_limit(self, silence):
        '''
        Returns a sample rate for the specified number of seconds.

        :param silence: int
            Seconds since last encounter.
        :returns: int
        '''
        if not Config.data['sample_times']:
            return 1
        for amount, sample_rate in Config.data['sample_times']:
            if silence >= amount:
                return sample_rate
        return Config.data['max_sample_time']

    def should_sample(self, times_seen, last_seen):
        '''
        Gets a sample rate for both times_seen and last_seen in seconds.
        Uses modulus to see if it should be sampled or not.

        :param times_seen: int
        :param last_seen: int
        :returns: boolean
        '''
        if not Config.data['sample_data']:
            return True
        if times_seen % self.count_limit(times_seen):
            return False
        if not last_seen:
            return True
        silence_timedelta = self.received - last_seen
        silence = silence_timedelta.days * 86400 + silence_timedelta.seconds
        if times_seen % self.time_limit(silence):
            return False
        return True

    def get_save_filters(self):
        '''
        Returns a list of those filters in `self.matched_filters`, 
        that has a save equals true.

        :return: list of tlog.base.filter.Filter
        '''
        save_filters = []
        for filter_ in self.matched_filters:
            if filter_.data.get('save', True):
                save_filters.append(filter_)
        return save_filters

    def save(self):
        '''
        Stores the object in the database.
        Returns None if there were no reason to sample the log message.

        :returns: boolean or None
        '''
        if not self.valid:
            return False
        save_filters = self.get_save_filters()
        if not save_filters:
            return False
        self.saved = False
        self.log_group = Log_group.add(self)
        self.update_count(save_filters)
        if self.should_sample(times_seen=self.log_group.times_seen, last_seen=self.log_group.last_seen):
            self.save_log()
            self.saved = True        
        Log_group_filters.add(save_filters, self.log_group.id)
        self.set_events()
        self.send_notification()
        self.send_to_elasticsearch()
        if self.saved:
            return True
        return None

    def send_notification(self):
        '''
        Sends notification if there haven't already in the allowed interval.

        :param session: db session
        '''
        if Log_group_notification_last_sent.check(log_group_id=self.log_group.id):
            Log_group_notification_last_sent.update(log_group_id=self.log_group.id)
            Notifier.send(
                message=self.data.get('message', '<no message>'),
                filters=self.matched_filters,
                store=self,
            )

    def update_count(self, save_filters):
        '''
        Updates counts for Times_seen_by_minute, Log group times seen and server times seen.

        :param session: db session
        :param save_filters: list of tlog.base.fliter.Filter
        '''
        with new_session() as session:
            try:
                for filter_ in save_filters:
                    Times_seen_by_minute._update(
                        session=session,
                        log_group_id=self.log_group.id, 
                        filter_id=filter_.id,
                    )
                Log_group._inc_seen(
                    session=session,
                    log_group=self.log_group
                )
                Server_count._add(
                    session=session,
                    log_group_id=self.log_group.id,
                    name=self.hostname,
                )
                session.commit()
            except IntegrityError as e:
                # try again
                logging.error(unicode(e))
                self.update_count(save_filters)

    def set_events(self):
        '''
        Addes a event under the right circumstances.

        :param session: db session
        '''
        if self.log_group.status == constants.STATUS_RESOLVED:
            Log_group.update_status(
                id_=self.log_group.id,
                status=constants.STATUS_UNRESOLVED,
                reopened=datetime.utcnow(),
            )
            Log_group_event.new(
                log_group_id=self.log_group.id,
                user_id=constants.SYSTEM_USER,
                message='reopened this log group'
            )

    def save_log(self):
        '''
        Inserts the log message to table `logs`.
        '''
        with new_session() as session:
            log = models.Log(
                hostname=self.hostname,
                external_id=self.external_id,
                message_hash=self.message_hash,
                received=self.received,
                data=json_dumps(self.data).encode('zlib').encode('base64'),
                level=self.level,
                log_group_id=self.log_group.id,
            )
            session.add(log)
            session.commit()
            Log_group._update_last_log_id(
                session=session,
                id_=self.log_group.id,
                last_log_id=log.id,
            )

    def send_to_elasticsearch(self):
        '''
        If enabled the received log message will be send to elasticsearch for indexing.
        '''
        if not Config.data['elasticsearch']['enabled']:
            return False
        filters = []
        filter_ids = []
        for filter_ in self.matched_filters:
            if filter_.data.get('searchable', False):
                filters.append(filter_)
                filter_ids.append(filter_.id)
        if not filters:
            return False
        data = {
            'hostname': self.hostname,
            'level': self.level,
            'received': self.received,
            'message_hash': self.message_hash,
            'data': self.data,
            'filters': filter_ids,
        }
        if self.log_group:
            data['log_group_id'] = self.log_group.id
        self.es.index(
            'logs', 
            'log', 
            data,
        )