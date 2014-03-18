# coding=UTF-8
import nose
import mock
import os
from unittest2 import TestCase
from tlog.testbase import Testbase
from tlog.base.user import User, User_team
from tlog.base.team import Team
from tlog.base.filter import Filter, Filter_team
from tlog.receiver.notifier import Notifier
from tlog.receiver.store import Store
from tlog.receiver.parse import Parse

class Mock_notifier(object):

    email_send = False

    @classmethod
    def mock_send_email(cls, to, message, filters, store=None):
        assert len(to) == 2
        assert to[0].email == u'test1@example.com'
        assert to[1].email == u'test3@example.com'
        assert filters[0].name == u'Test filter 1'
        cls.email_send = True
        return True

class test_notifier(Testbase):

    @mock.patch('tlog.receiver.notifier.Notifier.send_email', Mock_notifier.mock_send_email)
    def test_send(self):
        '''
        Creates 3 users, 2 teams and 2 filters.

        User 1 and 2 is a member of team 1 and user 2 is a member of team 2.
        Team 1 has a relation to both filter 1 and 2.
        Team 2 has a relation to filter 2.

        User 1 and 3 should receive an email and User 2 should not.
        '''
        user = User.new(
            name=u'Test user 1', 
            email='test1@example.com',
            notification_types={
                'send_email': {
                    'data': 'test1@example.com',
                    'enabled': True,
                }
            }
        )
        user2 = User.new(
            name=u'Test user 2', 
            email='test2@example.com',
            notification_types={
                'send_email': {
                    'data': 'test2@example.com',
                    'enabled': False,
                }
            }
        )
        user3 = User.new(
            name=u'Test user 3', 
            email='test3@example.com',
            notification_types={
                'send_email': {
                    'data': 'test3@example.com',
                    'enabled': True,
                }
            }
        )
        team = Team.new(
            name=u'Test team 1',
        )
        team2 = Team.new(
            name=u'Test team 2',
        )
        filter1 = Filter.new(
            name=u'Test filter 1', 
            data_yaml='notify: true',
        )
        filter2 = Filter.new(
            name=u'Test filter 2', 
            data_yaml='notify: false',
        )
        # create a relations
        User_team.new(
            team_id=team.id, 
            user_id=user.id
        )
        User_team.new(
            team_id=team2.id, 
            user_id=user2.id
        )
        User_team.new(
            team_id=team.id, 
            user_id=user3.id
        )
        Filter_team.new(
            filter_id=filter1.id, 
            team_id=team.id
        )
        Filter_team.new(
            filter_id=filter2.id, 
            team_id=team.id
        )
        Filter_team.new(
            filter_id=filter2.id, 
            team_id=team2.id
        )

        Mock_notifier.email_send = False
        Notifier.send(
            message='Test notification',
            filters=[
                filter1,
                filter2,
            ]
        )
        self.assertTrue(Mock_notifier.email_send)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)