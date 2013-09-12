import base
from tornado.web import authenticated
from tlog.base.log_group import Log_group, Log_group_filters
from tlog.base.event import Log_group_events, Log_group_event
from tlog.base.count import Servers_count
from tlog import constants
from tlog.base.log import Log
from datetime import datetime

class Handler(base.Handler):

    @authenticated
    def get(self, log_group_id, log_id=None):
        '''
        Shows a log group.
        '''
        log_group = Log_group.get_by_id(id_=int(log_group_id))
        if not log_group:
            self.error(404, 'Log group not found')
        if not log_id:
            log_id = -1
            if log_group.last_log_id:
                log_id = log_group.last_log_id
        log = Log.get(id_=log_id)
        self.render(
            'log_group_view.html',
            title='Log group',
            log_group=log_group,
            syslog_severity=constants.SYSLOG_SEVERITY,            
            syslog_facility=constants.SYSLOG_FACILITY,
            events=Log_group_events.get(log_group.id),
            log=log,
            servers=Servers_count.get(log_group.id),
            filters=Log_group_filters.get(log_group.id),
            prev_log=Log.get_prev(id_=log_id, log_group_id=log_group.id),
            next_log=Log.get_next(id_=log_id, log_group_id=log_group.id),
        )

class Status_handler(base.Handler): 

    @authenticated
    def post(self):
        '''
        Changes the status of a log group.
        '''
        log_group_id = int(self.get_argument('log_group_id'))
        status = int(self.get_argument('status'))
        if status <> constants.STATUS_RESOLVED and status <> constants.STATUS_UNRESOLVED:
            self.error(400, 'Unknown status {}'.format(status))
        log_group = Log_group.get_by_id(log_group_id)
        if log_group.status <> status:
            reopened = None
            if log_group.status == constants.STATUS_RESOLVED:
                reopened = datetime.utcnow()
            Log_group.update_status(
                id_=log_group_id,
                status=status,
                reopened=reopened,
            )
            if status == constants.STATUS_RESOLVED:
                Log_group_event.new(
                    log_group_id=log_group_id,
                    user_id=self.current_user.id,
                    message='marked this log group as resolved',
                )
            if status == constants.STATUS_UNRESOLVED:
                Log_group_event.new(
                    log_group_id=log_group_id,
                    user_id=self.current_user.id,
                    message='reopened this log group',
                )

class Delete_handler(base.Handler):

    @authenticated
    def get(self):
        '''
        Deletes a log group and all the relations to it.
        '''
        Log_group.delete(id_=int(self.get_argument('log_group_id')))
        self.redirect('/stream')
        return