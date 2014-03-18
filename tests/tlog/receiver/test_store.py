# coding=UTF-8
import nose
import mock
from tlog.testbase import Testbase
from tlog.receiver.store import Store
from tlog.receiver.parse import Parse
from tlog.base.filter import Filter
from tlog.base.event import Log_group_event
from tlog.base.log_group import Log_group
from tlog import constants
from datetime import datetime, timedelta
import math
import time

class Mock_log_group_event(object):

    log_group_id = -1
    user_id = -1
    message = None

    @classmethod
    def new(cls, log_group_id, user_id, message):
        cls.log_group_id = log_group_id
        cls.user_id = user_id
        cls.message = message

class test_store(Testbase):

    def assertStore(self, store, valid_save=True):
        self.assertEqual(store.save(), valid_save)
        if valid_save:
            self.assertEqual(store.hostname, u'mymachine.example.com')
            self.assertEqual(store.level, 2)

    def get_filter(self):
        return Filter.new(
            name=u'Test filter ø', 
            data_yaml='store: true',
        )

    def test_save(self):
        filter_ = self.get_filter()
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'), [filter_])
        self.assertStore(store, True)

        # Lets test if it works with some unicode letters!
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: Rød grød med fløde'), [filter_])
        self.assertStore(store, True)
        
        # Here comes a bullshit log message
        store = Store(Parse(u'I''m a bullshit log message...'), [filter_])
        self.assertStore(store, False)

    def test_count_limit(self):
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'))
        self.assertEqual(store.count_limit(50), 1)
        self.assertEqual(store.count_limit(51), 2)

    def test_time_limit(self):
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'))
        self.assertEqual(store.time_limit(12345), 1)
        self.assertEqual(store.time_limit(1), 10000)
        self.assertEqual(store.time_limit(60), 60)

    def test_should_sample(self):
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'))
        self.assertTrue(store.should_sample(times_seen=2, last_seen=None))
        self.assertTrue(store.should_sample(times_seen=50, last_seen=None))
        self.assertFalse(store.should_sample(times_seen=51, last_seen=None))
        self.assertTrue(store.should_sample(times_seen=52, last_seen=None))

    def test_get_save_filters(self):
        filter1 = self.get_filter()
        filter2 = self.get_filter()
        filter2.data['store'] = False
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'), [filter1, filter2])
        save_filters = store.get_save_filters()
        self.assertEqual(len(save_filters), 1)

    @mock.patch('tlog.base.event.Log_group_event.new', Mock_log_group_event.new)
    def test_set_events(self):
        filter_ = Filter.new(u'Test filter ø', data_yaml='store: true')
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'), [filter_])
        store.save()

        Log_group.update_status(
            id_=store.log_group.id,
            status=constants.STATUS_RESOLVED,
            reopened=None,
        )

        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su: BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'), [filter_])
        store.save()
        self.assertEqual(Mock_log_group_event.message, 'reopened this log group')

if __name__ == '__main__':
    nose.run(defaultTest=__name__)