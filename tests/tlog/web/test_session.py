# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.base.user import User
from tlog.web.session import Session

class test_session(Testbase):

    def test_new(self):
        user = User.new(
            name=u'Test user ø', 
            email='test5@example.com',
        )

        session = Session.new(user_id=user.id)
        self.assertTrue(isinstance(session, str))

    def test_get(self):
        user = User.new(
            name=u'Test user ø', 
            email='test6@example.com',
        )
        session = Session.new(user_id=user.id)
        user2 = Session.get(session_id=session)
        self.assertEqual(user.id, user2.id)

        # test expired
        session = Session.new(user_id=user.id, expire_days=-1)
        user2 = Session.get(session_id=session)
        self.assertEqual(user2, None)

    def test_delete(self):        
        user = User.new(
            name=u'Test user ø', 
            email='test6@example.com',
        )
        session = Session.new(user_id=user.id)
        user2 = Session.get(session_id=session)
        self.assertEqual(user.id, user2.id)

        self.assertTrue(
            Session.delete(session_id=session)
        )

        user2 = Session.get(session_id=session)
        self.assertEqual(user2, None)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)