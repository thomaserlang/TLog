# coding=UTF-8
import nose
import logging
from tlog.testbase import Testbase
from tlog.base.filter import Filter
from tlog.receiver.store import Store
from tlog.receiver.parse import Parse
from tlog.base.log_group import Log_group
from tlog.base.count import Times_seen_by_minute
from datetime import datetime, timedelta
from tlog.base.warning import Filter_warning, Filter_inactivity
from tlog.constants import MINUTE_NORMALIZATION
from tlog.utils import normalize_datetime
from tlog.decorators import new_session
from tlog import models

class test_filter_warning(Testbase):

    def test_get_filters_to_check(self):
        with new_session() as session:
            session.query(models.Filter).delete()
        '''
        Checks that `get_filters_to_check` only returns those filters that has been active in the latests interval.
        '''
        filter1 = Filter.new(u'Test filter 1', {
            'rate_warning': {
                'enabled': True,
                'min_logs': 100,
                'threshold': 500,
            }
        })
        filter2 = Filter.new(u'Test filter 1', {
            'rate_warning': {
                'enabled': True,                
                'min_logs': 100,
                'threshold': 500,
            }
        })
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group1 = Log_group.add(store)
        group1 = Log_group.get(message_hash=store.message_hash)
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group2 = Log_group.add(store)
        group2 = Log_group.get(message_hash=store.message_hash)

        # add som info that should not show up in the list we have to check for warnings.
        when = datetime.utcnow() - timedelta(minutes=MINUTE_NORMALIZATION)       
        Times_seen_by_minute.update(
            log_group_id=group1.id,
            filter_id=filter1.id,
            when=when,
            inc=25,
        )

        when = datetime.utcnow() - timedelta(minutes=10, seconds=30)     

        # checks that the filters groups correctly
        Times_seen_by_minute.update(
            log_group_id=group1.id,
            filter_id=filter1.id,
            when=when,
            inc=1000,
        )
        Times_seen_by_minute.update(
            log_group_id=group2.id,
            filter_id=filter1.id,
            when=when,
            inc=150,
        )

        # there should not be enough messages received for this filter to be checked for alerts.
        Times_seen_by_minute.update(
            log_group_id=group1.id,
            filter_id=filter2.id,
            when=when,
            inc=1000,
        )

        now = datetime.utcnow()
        from_date = now - timedelta(minutes=MINUTE_NORMALIZATION)
        filters_to_check = Filter_warning.get_filters_to_check()

        self.assertTrue(len(filters_to_check) > 0)
        self.assertEqual(filters_to_check[0].normalized_count, 100)

        return filters_to_check

    def test_check_filter_warning(self):
        with new_session() as session:
            session.query(models.Filter).delete()
        filter1 = Filter.new(u'Test filter 1', {
            'rate_warning': {
                'enabled': True,                
                'min_logs': 100,
                'threshold': 500,
            }
        })
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5123'))
        group1 = Log_group.add(store)

        # create some intervals
        intervals = 20
        now = datetime.utcnow()
        for i in xrange(1, intervals):
            Times_seen_by_minute.update(
                log_group_id=group1.id,
                filter_id=filter1.id,
                when=normalize_datetime(now - timedelta(minutes=(i * MINUTE_NORMALIZATION))),
                inc=1000 + 10 * i,
            )

        # create what would look like a lot of new messages in a short time. This should be enough to trigger then warning notification.
        when = datetime.utcnow() - timedelta(minutes=1, seconds=30)     
        Times_seen_by_minute.update(
            log_group_id=group1.id,
            filter_id=filter1.id,
            when=when,
            inc=1000,
        )

        filters_to_check = Filter_warning.get_filters_to_check()
        self.assertTrue(
            Filter_warning.check_filter_warning(filters_to_check[0]),
        )

class Test_inactivity(Testbase):

    def test_check(self):
        with new_session() as session:
            session.query(models.Filter).delete()
        filter1 = Filter.new(u'Test filter 1', {
            'inactivity': {
                'enabled': True,
                'minutes': 15,
            }
        })
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group1 = Log_group.add(store)
        group1 = Log_group.get(message_hash=store.message_hash)

        when = datetime.utcnow() - timedelta(minutes=16)     
        Times_seen_by_minute.update(
            log_group_id=group1.id,
            filter_id=filter1.id,
            when=when,
        )
        self.assertTrue(Filter_inactivity.check())

if __name__ == '__main__':
    nose.run(defaultTest=__name__)