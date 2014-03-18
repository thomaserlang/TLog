# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.receiver.store import Store
from tlog.base.count import Times_seen_by_minute, Server_count, Servers_count
from tlog.receiver.parse import Parse
from tlog.base.filter import Filter
from tlog.base.log_group import Log_group

class test_times_seen_by_minute(Testbase):

    def test_update(self):
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group = Log_group.add(store)
        filter_ = Filter.new(name=u'Test filter ø', data_yaml='')
        Times_seen_by_minute.update(
            log_group_id=group.id,
            filter_id=filter_.id,
        )

        minutes = Times_seen_by_minute.get_by_log_group_id(log_group_id=group.id)
        self.assertEqual(len(minutes), 1)
        self.assertEqual(minutes[0].times_seen, 1)

class test_server_count(Testbase):

    def test_add(self):
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5'))
        group = Log_group.add(store)
        group = Log_group.get(message_hash=store.message_hash)

        self.assertTrue(
            Server_count.add(
                log_group_id=group.id,
                name=store.hostname,
            )
        )
        self.assertTrue(
            Server_count.add(
                log_group_id=group.id,
                name=store.hostname,
            )
        )

        servers = Servers_count.get(log_group_id=group.id)
        self.assertEqual(len(servers), 1)
        self.assertEqual(servers[0].name, store.hostname)
        self.assertEqual(servers[0].count, 2)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)