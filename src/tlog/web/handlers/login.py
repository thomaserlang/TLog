import base
import tornado.web
import tornado.gen
import tornado.concurrent
from tlog.web import forms
from tlog.base.user import User
from tlog.web.session import Session

class Handler(base.Handler):

    def get(self):
        if self.current_user:
            self.redirect(self.get_argument('next', '/'))
        self.render(
            'login.html',
            title='Login',
            form=forms.Login(),
            errors=[],
        )

    def new_session(self, user_id, expire_days=30):
        '''
        Creates a new session for a user a sets the generated session_id in a secure cookie.

        :param user_id: int
        :param days: int
        '''
        session_id = Session.new(
            user_id=user_id, 
            expire_days=expire_days
        )
        self.set_secure_cookie(
            name='session_id', 
            value=session_id, 
            expires_days=expire_days,
        )
        return True

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        form = forms.Login(self.request.arguments)
        errors = []
        if form.validate():
            user = yield self.login(
                email=form.email.data, 
                password=form.password.data
            )
            if not user:
                errors.append('Wrong email or password')
            if not errors:
                self.new_session(user_id=user.id)
                self.redirect(self.get_argument('next', '/'))
                return
        self.render('login.html',
            title=u'Login',
            form=form,
            errors=errors,
        )

    @tornado.concurrent.run_on_executor
    def login(self, email, password):
        return User.login(
            email=email, 
            password=password,
        )