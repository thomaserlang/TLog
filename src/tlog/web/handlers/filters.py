import base
from tornado.web import authenticated
from tlog.base.filter import Filters

class Handler(base.Handler):

    @authenticated
    def get(self):
        filters = Filters.get()
        self.render(
            'filters.html', 
            title='Filters',
            filters=filters,
        )