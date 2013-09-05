import base
import json
from tlog.web import forms
from tornado.web import authenticated
from tlog.base.team import Team
from tlog.base.user import Users, User_team, Users_team

class New_handler(base.Handler):
    '''
    Handles the creation of a new team.
    '''

    @authenticated
    def get(self):
        '''
        Renders the create new team form.
        '''
        self.render(
            'team.html',
            title='New team',
            form=forms.Team(),
            edit=False,
        )

    @authenticated
    def post(self):
        '''
        Validates and creates a new team.
        Redirects to the new team if successful.
        '''
        form = forms.Team(self.request.arguments)
        if form.validate():
            team = Team.new(
                name=form.name.data,
            )
            self.redirect('/team/{}'.format(team.id))
            return
        self.render(
            'team.html',
            title='New team',
            form=form,
            edit=False,
        )

class Edit_handler(base.Handler):
    '''
    Handles the editing of a team.
    '''

    @authenticated
    def get(self, team_id):
        '''
        Renders the edit team form. 

        :param team_id: int
        '''
        team = Team.get(id_=team_id)
        if not team:
            self.error(404, 'Team not found')
        form = forms.Team()
        form.name.data = team.name
        self.render(
            'team.html',
            title=u'Team: {}'.format(team.name),
            form=form,
            edit=True,
            users=Users.get(),
            team=team,
            members=Users_team.get(team_id=team_id),
        )

    @authenticated
    def post(self, team_id):
        '''
        Validates and updates the team.
        Redirects to the new team if successful.

        :param team_id: int
        '''
        team = Team.get(id_=team_id)
        if not team:
            self.error(404, 'Team not found')
        form = forms.Team(self.request.arguments)
        if form.validate():
            Team.update(
                id_=team_id,
                name=form.name.data, 
            )
            self.redirect('/team/{}'.format(team.id))
            return
        self.render(
            'team.html',
            title='New team',
            form=form,
            edit=True,
            users=Users.get(),
            team=team,
            members=Users_team.get(team_id=team_id),
        )

class Add_member_handler(base.Handler):

    @authenticated
    def post(self, team_id):
        user_id = int(self.get_argument('user_id', 0))
        User_team.new(
            team_id=team_id,
            user_id=user_id,
        )
        self.redirect('/team/{}'.format(team_id))

class Remove_member_handler(base.Handler):

    @authenticated
    def get(self, team_id):
        user_id = int(self.get_argument('user_id', 0))
        User_team.delete(
            team_id=team_id,
            user_id=user_id,
        )
        self.redirect('/team/{}'.format(team_id))