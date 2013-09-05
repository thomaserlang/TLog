import tornado.web
import tornado.escape
import json
import httplib
from tlog.web.session import Session
from tlog import utils

class Handler(tornado.web.RequestHandler):

    def error(self, error_code, error_msg):
        raise tornado.web.HTTPError(error_code, error_msg)

    def k_formatter(self, number):
        '''
        Turns 1000 into 1k
        :param number: int
        :returns: string
        '''
        if number > 999:
            return '{:10.2f}k'.format(number/float(1000))
        return '{}'.format(number)

    def get_template_namespace(self):
        namespace = tornado.web.RequestHandler.get_template_namespace(self)
        namespace.update(
            title='TLOG',
            k_formatter=self.k_formatter,
        )
        return namespace

    def get_current_user(self):
        session_id = self.get_secure_cookie('session_id')
        if session_id:
            return Session.get(session_id=session_id)
        return None

    @property
    def executor(self):
        return self.application.executor

class API_HTML_Handler(Handler):

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.set_header("Content-Type", "text/html")        

class API_handler(Handler):

    def set_default_headers(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', 'Sat, 26 Jul 1997 05:00:00 GMT')
        self.set_header("Content-Type", "application/json")

    def check_xsrf_cookie(self):
        '''
        We do not need xsrf protection for the API.
        '''
        pass

    def write_error(self, status_code, **kwargs):
        if 'error_msg' in kwargs:
           error = {'msg': kwargs['error_msg']}
        else:
            error = {'msg': httplib.responses[status_code]}
        self.write(tornado.escape.json_encode(error))

    def write_object(self, obj):
        self.write(
            json.dumps(
                obj,
                cls=utils.JsonEncoder,
            ).replace("</", "<\\/")
        )