# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.receiver.store import Store
from tlog.base.log_group import Log_group, Log_groups, Log_group_filters
from tlog.receiver.parse import Parse
from tlog.base.filter import Filter

class test_log_group(Testbase):

    def test_add(self):
        '''
        Checks the `Log_group.add` can group the same log event 3 times.
        '''
        def test_add(times_seen):
            store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
            Log_group.add(store)
            group = Log_group.get(message_hash=store.message_hash)
            Log_group.inc_seen(log_group=group)
            group = Log_group.get(message_hash=store.message_hash)
            self.assertEqual(group.times_seen, times_seen)

        for i in [1,2,3]:
            test_add(i)

class test_log_groups(Testbase):

    def test_get(self):
        '''
        Creates 2 filters and creates a relation between the filters a a log_group.
        Tests that both strict and non strict version works.
        '''

        filter1 = Filter.new(name=u'Test filter 1', data={})
        filter2 = Filter.new(name=u'Test filter 2', data={})
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group = Log_group.add(store)
        group = Log_group.get(message_hash=store.message_hash)
        self.assertTrue(
            Log_group_filters.add(
                filters=[filter1, filter2],
                log_group_id=group.id,
            )
        )
        groups = Log_groups.get(
            filters = [filter1, filter2],
        )
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].id, group.id)


        # test that the strict version also works.
        filter2.update(id_=filter2.id, name='Test filter asd', data={})
        filter2 = Filter.get(id_=filter2.id)
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - NEW MESSAGE ZwPpeQyUtrRKxw5'))
        group = Log_group.add(store)
        group = Log_group.get(message_hash=store.message_hash)
        self.assertTrue(
            Log_group_filters.add(
                filters=[filter1, filter2],
                log_group_id=group.id,
            )
        )

        groups = Log_groups.get(
            filters = [filter2],
        )
        self.assertEqual(len(groups), 2)

        groups = Log_groups.get(
            filters = [filter2],
            strict_version = True,
        )

        self.assertEqual(len(groups), 1)

class test_filters_log_group(Testbase):

    def test_add(self):
        filter1 = Filter.new(name=u'Test filter 1', data={})
        filter2 = Filter.new(name=u'Test filter 2', data={})
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group = Log_group.add(store)
        group = Log_group.get(message_hash=store.message_hash)
        self.assertTrue(
            Log_group_filters.add(
                filters=[filter1, filter2],
                log_group_id=group.id,
            )
        )

        # test get
        filters = Log_group_filters.get(log_group_id=group.id)
        self.assertEqual(len(filters), 2)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)