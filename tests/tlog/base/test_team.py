# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.base.team import Team, Team_exception_duplicate_name

class test_team(Testbase):

    def new_team(self):
        return Team.new(
            name=u'Test team ø',
        )

    def assertTeam(self, team):
        self.assertEqual(team.name, u'Test team ø')
        self.assertTrue(team.id > 0)

    def test_new(self):
        team = self.new_team()
        self.assertTeam(team)

    def test_new_duplicate(self):
        team = self.new_team()
        try:
            team2 = self.new_team()
            self.assertTrue(False, 'Duplicate team names must not be allowed.')
        except Team_exception_duplicate_name:
            pass

    def test_get(self):
        team = self.new_team()
        team = Team.get(id_=team.id)
        self.assertTeam(team)

    def test_get_by_name(self):
        team = self.new_team()
        team = Team.get_by_name(name=team.name)
        self.assertTeam(team)

    def test_update(self):
        team = self.new_team()
        Team.update(
            id_=team.id,
            name='Test 2'
        )
        team = Team.get(id_=team.id)
        self.assertEqual(team.name, u'Test 2')


if __name__ == '__main__':
    nose.run(defaultTest=__name__)