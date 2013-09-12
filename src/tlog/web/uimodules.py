import tornado.web
from datetime import datetime, timedelta
from tlog.decorators import new_session
from tlog import models
from itertools import groupby

class Form(tornado.web.UIModule):
  '''
  Generic form rendering module. Works with wtforms.
  Use this in your template code as:

  {% module Form(form) %}

  where `form` is a wtforms.Form object. Note that this module does not render
  <form> tag and any buttons.
  '''

  def render(self, form):
    return self.render_string('form.html', form=form)

class Log_chart(tornado.web.UIModule):

    def render(self, url, height=100):
        '''
        :param url: str
        :param height: int
        '''
        return self.render_string(
            'log_chart.html',
            url=url,
            height=height,
        )
       