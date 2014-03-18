import logging
from parse import Parse
from tlog.base.filter import Filters
from filter_checker import Filters_checker
from store import Store
from tlog.base.watchdog import Watchdog

class Receiver(object):
    
    @classmethod
    def add(cls, data):
        '''
        :param data: str
        :returns: boolean
        '''
        cls.check_for_heartbeat_request(data)
        parsed = Parse(data)
        if not parsed:
            logging.notice('Unable to parse log message: {}'.format(data))
            return False
        filters = Filters.get()
        matched_filters = Filters_checker.check(
            filters=filters, 
            parsed=parsed,
        )
        store = Store(parsed=parsed, matched_filters=matched_filters)
        if not store.save():
            return False
        return True

    @classmethod
    def check_for_heartbeat_request(cls, data):
        if data == 'TLOG_HEARTBEAT':
            Watchdog.pong()