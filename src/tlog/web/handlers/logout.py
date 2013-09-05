import base
from tlog.web.session import Session
from tornado.web import authenticated

class Handler(base.Handler):

    @authenticated
    def get(self):
        session_id = self.get_secure_cookie('session_id')
        if session_id:
            Session.delete(
                session_id=session_id
            )
            self.clear_cookie("session_id")
        self.redirect('/')