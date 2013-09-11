import base
from tornado.web import authenticated
from tlog.base.log_group import Log_groups
from tlog.base.filter import Filters_user, Filter
from tlog import constants
from tlog import models
from datetime import datetime, timedelta

class Handler(base.Handler):

    @authenticated
    def get(self):
        self.render(
            'frontpage.html', 
            title="TLog",
            log_groups=Log_groups.get(
                filters=Filters_user.get(user_id=self.current_user.id),
                extra_filter=[
                    models.Log_group.last_seen>=datetime.utcnow()-timedelta(hours=24),
                ],
                limit=constants.LOG_GROUP_PER_PAGE,
                order_by=[
                    constants.LOG_GROUP_ORDER_BYS[constants.LOG_GROUP_ORDER_BY_LAST_SEEN],
                ],
            ),
            syslog_severity=constants.SYSLOG_SEVERITY,
        )