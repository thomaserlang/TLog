import base
from tornado.web import authenticated

class Handler(base.Handler):

    @authenticated
    def get(self):
        self.render('frontpage.html', title="TLog")