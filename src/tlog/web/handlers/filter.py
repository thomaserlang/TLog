import base
import json
from tlog.web import forms
from tornado.web import authenticated
from tlog.base.filter import Filter, Filter_team
from tlog.base.team import Teams
from tlog.base.count import Times_seen_by_minute

class New_handler(base.Handler):
    '''
    Handles the creation of new filters.
    '''

    @authenticated
    def get(self):
        '''
        Renders the create new filter form.
        '''
        form = forms.Filter()
        form.data.data = json.dumps(
            {
                "match": {},
                "notmatch": {},
                "store": True,
                "notify": False,
                "searchable": False,
            }
        )
        self.render(
            'filter.html',
            title='New filter',
            form=form,
            edit=False,
        )

    @authenticated
    def post(self):
        '''
        Validates and creates a new filter.
        Redirects to the new filter if successful.
        '''
        form = forms.Filter(self.request.arguments)
        if form.validate():
            filter_ = Filter.new(
                name=form.name.data, 
                data=json.loads(form.data.data),
            )
            self.redirect('/filter/{}'.format(filter_.id))
            return
        self.render(
            'filter.html',
            title='New filter',
            form=form,
            edit=False,
        )

class Edit_handler(base.Handler):
    '''
    Handles the editing of a filter.
    '''

    @authenticated
    def get(self, filter_id):
        '''
        Renders the edit filter form. 

        :param filter_id: int
        '''
        filter_ = Filter.get(id_=filter_id)
        if not filter_:
            self.error(404, 'Filter not found')
        form = forms.Filter()
        form.name.data = filter_.name
        form.data.data = json.dumps(filter_.data)
        self.render(
            'filter.html',
            title=u'Filter: {}'.format(filter_.name),
            form=form,
            edit=True,
            filter=filter_,
            members=Filter_team.get_teams_by_filter_id(filter_id=filter_id),
            teams=Teams.get(),
            logs_per_minute=Times_seen_by_minute.get_logs_per_minute(filter_id=filter_.id),
        )

    @authenticated
    def post(self, filter_id):
        '''
        Validates and updates the filter.
        Redirects to the new filter if successful.

        :param filter_id: int
        '''
        filter_ = Filter.get(id_=filter_id)
        if not filter_:
            self.error(404, 'Filter not found')
        form = forms.Filter(self.request.arguments)
        if form.validate():
            filter_.name = form.name.data
            filter_.data = json.loads(form.data.data)
            Filter.update(
                id_=filter_id,
                name=filter_.name , 
                data=filter_.data,
            )
            self.redirect('/filter/{}'.format(filter_.id))
            return
        self.render(
            'filter.html',
            title='New filter',
            form=form,
            edit=True,
            filter=filter_,
            members=Filter_team.get_teams_by_filter_id(filter_id=filter_id),
            teams=Teams.get(),
            logs_per_minute=Times_seen_by_minute.get_logs_per_minute(filter_id=filter_.id),
        )

class Add_member_handler(base.Handler):

    @authenticated
    def post(self, filter_id):
        team_id = int(self.get_argument('team_id', 0))
        Filter_team.new(
            team_id=team_id,
            filter_id=filter_id,
        )
        self.redirect('/filter/{}'.format(filter_id))

class Remove_member_handler(base.Handler):

    @authenticated
    def get(self, filter_id):
        team_id = int(self.get_argument('team_id', 0))
        Filter_team.delete(
            filter_id=filter_id,
            team_id=team_id,
        )
        self.redirect('/filter/{}'.format(filter_id))