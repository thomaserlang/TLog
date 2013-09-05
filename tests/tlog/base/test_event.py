# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.base.log_group import Log_group
from tlog.base.user import User
from tlog.base.event import Log_group_event, Log_group_events
from tlog.receiver.store import Store
from tlog.receiver.parse import Parse

class test_log_group_event(Testbase):

    def test_new(self):
        user = User.new(
            name=u'Test user ø', 
            email='test@example.com',
        )
        store = Store(Parse(u'<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - ZwPpeQyUtrRKxw5asd'))
        Log_group.add(store)
        group = Log_group.get(message_hash=store.message_hash)

        self.assertTrue(
            Log_group_event.new(
                log_group_id=group.id,
                user_id=user.id,
                message=u'Test event',
            )
        )
        self.assertTrue(
            Log_group_event.new(
                log_group_id=group.id,
                user_id=user.id,
                message=u'Test event 2',
            )
        )
        events = Log_group_events.get(log_group_id=group.id)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].user.id, user.id)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)