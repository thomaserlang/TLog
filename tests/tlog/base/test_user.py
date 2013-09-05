# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.base.user import User, User_exception_duplicate_email, User_team, Users_team, User_teams
from tlog.base.team import Team

class test_user(Testbase):

    def new_user(self, email='test@example.com'):
        return User.new(
            name=u'Test user ø', 
            email=email,
        )

    def assertUser(self, user):
        self.assertTrue(user.id > 0)
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, u'Test user ø')

    def test_new(self):
        user = self.new_user()
        self.assertUser(user)

    def test_new_duplicate(self):
        user = self.new_user()
        try:
            user2 = self.new_user()
            self.assertTrue(False, 'Duplicate email addresses must not be allowed!')
        except User_exception_duplicate_email:
            pass

    def test_get(self):
        user = self.new_user()
        user = User.get(id_=user.id)
        self.assertUser(user)

    def test_get_by_email(self):
        user = self.new_user()
        user = User.get_by_email(email=user.email)
        self.assertUser(user)

    def test_change_password(self):
        user = self.new_user()
        self.assertTrue(
            User.change_password(
                id_=user.id, 
                password=u'hejhejø123',
            )
        )
        self.assertFalse(
            User.change_password(
                id_=user.id, 
                password=u'asdasd',
                current_password=u'WRONG_PASSWORD',
            )
        )
        self.assertTrue(
            User.change_password(
                id_=user.id, 
                password=u'asdasd',
                current_password=u'hejhejø123',
            )
        )
        self.assertTrue(
            User.verify_password(
                id_=user.id, 
                password=u'asdasd',
            )
        )

    def test_verify_password(self):
        user = self.new_user()
        self.assertTrue(
            User.change_password(
                id_=user.id, 
                password=u'hejhejø123',
            )
        )
        self.assertTrue(
            User.verify_password(
                id_=user.id, 
                password=u'hejhejø123',
            )
        )
        self.assertFalse(
            User.verify_password(
                id_=user.id, 
                password=u'WRONG_PASSWORD',
            )
        )

class test_user_team(test_user):

    def test_new(self):
        user = self.new_user()
        team = Team.new(
            name='Test team', 
        )
        self.assertTrue(
            User_team.new(
                user_id=user.id,
                team_id=team.id,
            )
        )
        teams = User_teams.get(user_id=user.id)
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].id, team.id)

        users = Users_team.get(team_id=team.id)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].id, user.id)

        users = Users_team.get_by_team_list(teams=[team])
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].id, user.id)

    def test_delete(self):
        user = self.new_user()
        team = Team.new(
            name='Test team', 
        )
        self.assertTrue(
            User_team.new(
                user_id=user.id,
                team_id=team.id,
            )
        )
        teams = User_teams.get(user_id=user.id)
        self.assertEqual(len(teams), 1)
        self.assertEqual(teams[0].id, team.id)

        self.assertTrue(
            User_team.delete(user_id=user.id, team_id=team.id)
        )
        teams = User_teams.get(user_id=user.id)
        self.assertEqual(len(teams), 0)

class test_user_teams(Testbase):
    '''
    See test_user_team.test_new
    '''

class test_users_teams(Testbase):
    '''
    See test_user_team.test_new
    '''

if __name__ == '__main__':
    nose.run(defaultTest=__name__)