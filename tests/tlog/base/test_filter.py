# coding=UTF-8
import nose
from tlog.testbase import Testbase
from tlog.base.filter import Filter, Filter_version, Filters, Filter_team
from tlog.base.team import Team
from tlog.receiver.store import Store
from tlog.receiver.parse import Parse
from tlog.base.log_group import Log_group

class test_filter(Testbase):

    def check_filter_version(self, filter_id, version, data):
        '''
        Checks that a filter version has been created.

        :param filter_id: int
        :param version: int
        :param data: dict
        '''
        filter_version = Filter_version.get(
            filter_id=filter_id,
            version=version,
        )
        self.assertEqual(data, filter_version.data)

    def test_new(self):
        filter_ = Filter.new(name=u'Test filter ø', data_yaml='{}')
        self.assertTrue(filter_.id>0)
        self.assertEqual(filter_.name, u'Test filter ø')
        self.assertTrue(isinstance(filter_.data, dict))

        self.check_filter_version(filter_.id, filter_.version, filter_.data)


    def test_update(self):
        filter_ = Filter.new(name=u'Test filter ø', data_yaml='')
        Filter.update(
            id_=filter_.id,
            name=u'Test filter 2 ø',
            data_yaml='{}'
        )
        filter2 = Filter.get(id_=filter_.id)
        self.assertTrue(filter2.id>0)
        self.assertEqual(filter2.name, u'Test filter 2 ø')
        self.assertTrue(isinstance(filter2.data, dict))

        self.check_filter_version(filter2.id, filter2.version, filter2.data)

class test_filter_version(Testbase):
    '''
    See the test_filter.check_filter_version 
    '''

class test_filter_team(Testbase):

    def test(self):
        # new
        filter_ = Filter.new(name=u'Test filter ø', data_yaml='')
        team = Team.new(name=u'Test team ø')

        self.assertTrue(
            Filter_team.new(
                filter_id=filter_.id,
                team_id=team.id,
            )
        )

        # get teams by filter_id
        teams = Filter_team.get_teams_by_filter_id(filter_id=filter_.id)
        self.assertEqual(len(teams), 1)
        self.assertEqual(team.id, teams[0].id)

        # delete
        self.assertTrue(
            Filter_team.delete(
                filter_id=filter_.id,
                team_id=team.id,
            )
        )
        teams = Filter_team.get_teams_by_filter_id(filter_id=filter_.id)
        self.assertEqual(len(teams), 0)

class test_filters(Testbase):

    def test_get(self):
        Filter.new(u'Test filter ø', data_yaml='')
        filters = Filters.get()
        self.assertTrue(len(filters)>0)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)