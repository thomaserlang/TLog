import base
from tornado.web import authenticated
from tlog.base.user import User
from tlog.constants import NOTIFICATION_TYPES
import logging

class Info_handler(base.Handler):

    @authenticated
    def get(self):
        self.render(
            'settings_info.html',
            title='Settings - Info',
        )

class Notification_handler(base.Handler):

    @authenticated
    def get(self):
        self.render(
            'settings_notification.html',
            title='Settings - Notification',
            notification_types=NOTIFICATION_TYPES,
        )

    @authenticated
    def post(self):
        notification_types = {}
        for type_ in self.get_arguments('send_type_enabled'):
            notification_types[type_] = {
                'enabled': True,
                'data': self.get_argument(type_, ''),
            }
        User.update_notification_types(
            id_=self.current_user.id,
            notification_types=notification_types,
        )
        self.redirect('/settings/notification')
        return