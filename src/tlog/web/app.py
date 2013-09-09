from tlog.config import Config
Config.load()
import tornado.web
import tornado.httpserver
import tornado.ioloop
import uimodules
import futures
import os
import handlers.login
import handlers.frontpage
import handlers.logout
import handlers.filters
import handlers.filter
import handlers.teams
import handlers.team
import handlers.settings
import handlers.stream
import handlers.log_group
import handlers.search
import handlers.chart_data
import handlers.signup
from tlog.logger import logger
from tornado.options import define, options

class Application(tornado.web.Application):

    def __init__(self, **args):
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=static_path,
            debug=Config.data['debug'],
            autoescape=None,
            cookie_secret=Config.data['web']['cookie_secret'],
            login_url='/login',
            xsrf_cookies=True,
            ui_modules={
                'Form': uimodules.Form,
                'Log_chart': uimodules.Log_chart,
            },
        )
        urls = [
            (r'/favicon.ico', tornado.web.StaticFileHandler, {'path': os.path.join(static_path, 'favicon.ico')}),
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': static_path}),
            (r'/login', handlers.login.Handler),
            (r'/logout', handlers.logout.Handler),
            (r'/signup', handlers.signup.Handler),
            (r'/', handlers.frontpage.Handler),
            
            (r'/filters', handlers.filters.Handler),
            (r'/filter/new', handlers.filter.New_handler),
            (r'/filter/([0-9]+)', handlers.filter.Edit_handler),
            (r'/filter/([0-9]+)/add_member', handlers.filter.Add_member_handler),
            (r'/filter/([0-9]+)/remove_member', handlers.filter.Remove_member_handler),

            (r'/teams', handlers.teams.Handler),
            (r'/team/new', handlers.team.New_handler),
            (r'/team/([0-9]+)', handlers.team.Edit_handler),
            (r'/team/([0-9]+)/add_member', handlers.team.Add_member_handler),
            (r'/team/([0-9]+)/remove_member', handlers.team.Remove_member_handler),

            (r'/settings', handlers.settings.Notification_handler),
            (r'/settings/info', handlers.settings.Info_handler),
            (r'/settings/notification', handlers.settings.Notification_handler),

            (r'/stream', handlers.stream.Handler),
            (r'/stream/log_groups', handlers.stream.Log_groups_handler),

            (r'/log_group/([0-9]+)', handlers.log_group.Handler),
            (r'/log_group/([0-9]+)/([0-9]+)', handlers.log_group.Handler),
            (r'/log_group/change_status', handlers.log_group.Status_handler),     
            (r'/log_group_delete', handlers.log_group.Delete_handler),    

            (r'/search', handlers.search.Handler),    

            (r'/api/1/chart_data/times_seen_log_group/([0-9]+)', handlers.chart_data.Times_seen_log_group_handler),    
            (r'/api/1/chart_data/times_seen_filter/([0-9]+)', handlers.chart_data.Times_seen_filter_handler),
            (r'/api/1/chart_data/times_seen_user_filters', handlers.chart_data.Times_seen_user_filters_handler),
        ]
        self.executor = futures.ThreadPoolExecutor(Config.data['web']['pool_size'])

        tornado.web.Application.__init__(self, urls, **settings)

def main():
    define("port", default=Config.data['web']['port'], help="run on the given port", type=int)
    options.parse_command_line()
    logger.set_logger('web-{}.log'.format(options.port))
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()