import login
from tlog.web import forms
from tlog.base.user import User, User_exception_duplicate_email
import tornado.web
import tornado.gen
import tornado.concurrent

class Handler(login.Handler):

    def get(self):
        if self.current_user:
            self.redirect(self.get_argument('next', '/'))
        self.render(
            'signup.html',
            title='Signup',
            form=forms.Signup(),
            errors=[],
        )

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        form = forms.Signup(self.request.arguments)
        if form.validate():
            try:
                user = User.new(
                    name=form.name.data,
                    email=form.email.data,
                    notification_types={
                        'send_email': {
                            'enabled': True,
                            'data': form.email.data,
                        }
                    }
                )
                yield self.change_password(
                    user_id=user.id,
                    password=form.password.data,
                )
                self.new_session(
                    user_id=user.id,
                )
                self.redirect(self.get_argument('next', '/'))
                return
            except User_exception_duplicate_email as e:
                form.email.errors.append(e.message)
        self.render(
            'signup.html',
            title='Signup',
            form=form,
        )

    @tornado.concurrent.run_on_executor
    def change_password(self, user_id, password):
        User.change_password(
            id_=user_id,
            password=password,
        )