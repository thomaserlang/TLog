import base
from tornado.web import authenticated
from tlog.base.team import Teams

class Handler(base.Handler):

    @authenticated
    def get(self):
        teams = Teams.get()
        self.render(
            'teams.html', 
            title='Teams',
            teams=teams,
        )