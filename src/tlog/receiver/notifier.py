import smtplib
import tornado.template
import urlparse
import logging
from tlog.base.filter import Filter_team
from tlog.base.user import Users_team
from tlog.constants import SYSLOG_SEVERITY
from tlog.config import Config
from email.mime.text import MIMEText
from tlog.mail import Mail
from tlog.pushover import Pushover

class Notifier(object):
    '''
    Notifier sends notifications the way each user has specified how they would like to receive them.
 
    To add a new notification type you have to create a new method called `send_{some name}`.
    Then add the new notification type (with a help message) to the database table `notification_types`.
    Then each user can go to their setting page and enable which notification types, they would like to receive.
    '''

    @classmethod
    def send(cls, message, filters, store=None):
        '''
        Sends notifications to teams that are member of filters.

        Each filter can have x number of teams which can have x number of users in it.
        Each user can have x number of notification types.
        To prevent that x number of filters, with the same teams assigned, sends the same notification x times, 
        we have to group the users for each type of notification and send the notifications, when we have been through all the filters.
        This will also make sure that the users get the correct notifications, specified in there profile.

        :param message: str
            Custom message to be sent.
        :param filters: list of tlog.base.filter.Filter
        :param store: tlog.receiver.store.Store
            Specify `store` if any information should used from the stored log message.
        '''
        user_ids = []
        send_types = {}
        notify_filters = []
        for filter_ in filters:
            if filter_.data.get('notify', True):
                notify_filters.append(filter_)
                users = Users_team.get_by_team_list(
                    Filter_team.get_teams_by_filter_id(filter_id=filter_.id)
                )
                for user in users:
                    for send_type in user.notification_types:                        
                        if not user.notification_types[send_type].get('enabled', True):
                            continue
                        send_types.setdefault(send_type, {
                            'users': [],
                            'user_ids': [],
                        })
                        if user.id not in send_types[send_type]['user_ids']:# check for duplicated users. Stupid to send the same form of notification twice.                              
                            send_types[send_type]['users'].append(user)
                            send_types[send_type]['user_ids'].append(user.id)
        for send_type in send_types:
            if hasattr(cls, send_type):
                method = getattr(cls, send_type)
                if method:
                    to = []
                    try:
                        method(
                            to=send_types[send_type]['users'],
                            message=message,
                            filters=notify_filters,
                            store=store,
                        )
                    except Exception as e:
                        logging.error(u'Send type "{}" failed with error: {}'.format(send_type, unicode(e)))

    @classmethod
    def send_email(cls, to, message, filters, store=None):
        '''
        Sends a email to each user in `to`.

        :param to: list of tlog.base.user.User
        :param message: str
        :param filters: list of tlog.base.filter.Filter
        :param store: tlog.receiver.store.Store
            Specify `store` if any information should used from the stored log message.
        '''
        recipients = []
        for user in to:
            recipients.append(user.notification_types.get('send_email')['data'])

        template = tornado.template.Template(
            '''
            <html>
                <body>
                    <p style="font-size:14px;">{{ message }}</p>
                    <table>
                        {% if severity %} 
                        <tr>
                            <th align="right">Level:</th><td>{{ severity }}</td>
                        </tr>
                        {% end %}
                        {% if store %}
                            <tr>
                                <th align="right">Server:</th><td>{{ store.hostname }}</td>
                            </tr>
                            <tr>
                                <th align="right">External id:</th><td>{{ store.external_id }}</td>
                            </tr>
                            <tr>
                                <th align="right">Message hash:</th><td>{{ store.message_hash }}</td>
                            </tr>
                            <tr>
                                <th align="right">Times seen:</th><td>{{ store.log_group.times_seen + 1 }}</td>
                            </tr>
                            <tr>
                                <th align="right">URL:</th><td><a href="{{ urljoin(base_url, '/log_group/{}'.format(store.log_group.id)) }}">{{ urljoin(base_url, '/log_group/{}'.format(store.log_group.id)) }}</a></td>
                            </tr>
                        {% end %}
                    </table>
                    <p>You received this message because of the following filters:</p>
                    <table>
                        {% for filter_ in filters %}
                            <tr>
                                <td><a href="{{ urljoin(base_url, '/filter/{}'.format(filter_.id)) }}">{{ filter_.name }}</a></td>
                            </tr>
                        {% end %}
                    </table>
                </body>
            </html>
            '''
        )

        severity = SYSLOG_SEVERITY[4]
        if store:
            severity = SYSLOG_SEVERITY[store.level]
        Mail.send(
            recipients=recipients,
            subject='{}: {}'.format(severity, message),
            message=template.generate(
                severity=severity, 
                message=message, 
                filters=filters,
                store=store,
                base_url=Config.data['url'],
                urljoin=urlparse.urljoin,
            ),
        )
        return True

    @classmethod
    def send_pushover(cls, to, message, filters, store=None):
        '''
        Sends a pushover notification to each user in `to`.

        :param to: list of tlog.base.user.User
        :param message: str
        :param filters: list of tlog.base.filter.Filter
        :param store: tlog.receiver.store.Store
            Specify `store` if any information should used from the stored log message.
        '''
        severity_level = 4
        title = SYSLOG_SEVERITY[4]
        if store:
            severity_level = store.level
            title = SYSLOG_SEVERITY[severity_level]
        url = None
        if store:
            url = urlparse.urljoin(Config.data['url'], '/log_group/{}'.format(store.log_group.id)),
        for user in to:
            if 'send_pushover' in user.notification_types:
                Pushover.send(
                    user_key = user.notification_types['send_pushover']['data'], 
                    title=title,
                    message=message,
                    severity_level=severity_level,
                    url=url,
                )
                