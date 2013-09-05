import base
from tornado.web import authenticated
from tlog.base.filter import Filters_user, Filter
from tlog.base.log_group import Log_groups
from tlog import models
from tlog import constants

class Handler(base.Handler):
    
    @authenticated
    def get(self):
        filters = Filters_user.get(user_id=self.current_user.id)
        self.render(
            'stream.html',
            title='Stream',
            filters=filters,
            status_levels=constants.STATUS_LEVELS,
            status_default=constants.STATUS_UNRESOLVED,
            order_by_names=constants.LOG_GROUP_ORDER_BY_NAMES,
            order_by_default=constants.LOG_GROUP_ORDER_BY_DEFAULT,
            syslog_severity=constants.SYSLOG_SEVERITY,
        )

class Log_groups_handler(base.API_HTML_Handler):

    @authenticated
    def get(self):
        log_groups = Log_groups.get(
            filters=self._get_filters(),
            extra_filter=[
                models.Log_group.status == self._get_status(),
            ],
            limit=constants.LOG_GROUP_PER_PAGE,
            offset=self._get_offset(),
            order_by=[
                constants.LOG_GROUP_ORDER_BYS[self._get_order_by()],
            ]
        )

        self.render(
            'log_groups.html',
            title='Stream',
            log_groups=log_groups,
            syslog_severity=constants.SYSLOG_SEVERITY,
        )

    def _get_order_by(self): 
        '''
        Returns a order_by id.
        Usage: constants.LOG_GROUP_ORDER_BYS[self._get_order_by()]
        Returns constants.LOG_GROUP_ORDER_BY_DEFAULT if there is nothing set or a unknown id has been used.

        :returns: tlog.constants.LOG_GROUP_ORDER_BY
        '''
        return int(self.get_argument('order_by', constants.LOG_GROUP_ORDER_BY_DEFAULT))

    def _get_filters(self):
        '''
        If the filter_id argument is set, only log groups matching it will be shown.
        Otherwise all the users filters will be used.

        :returns list of tlog.base.filter.Filter
        '''
        filter_id = self.get_argument('filter_id', None)
        if not filter_id:
            return Filters_user.get(user_id=self.current_user.id)
        else:
            return [Filter.get(id_=filter_id)]

    def _get_status(self):
        '''
        :returns: int
        '''
        status = self.get_argument('status', None)
        if not status:
            return constants.STATUS_UNRESOLVED
        return int(status)

    def _get_offset(self):
        '''
        :returns: int
        '''
        page = int(self.get_argument('page', 0))
        if page < 0:
            page = 0
        return page * constants.LOG_GROUP_PER_PAGE