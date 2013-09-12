import requests
import logging
from tlog.config import Config

class Pushover(object):

    @classmethod
    def send(cls, user_key, title, message, severity_level, url=None):
        '''
        :param to: str 
            pushover user key
        :param title: str
        :param message: str
        :param severity_level: int
        :param url: str - Default: None
        :returns: boolean
        '''
        if not Config.data['pushover']['enabled']:
            logging.notice('pushover is not enabled in the config.')
            return False
        if severity_level < 3:
            priority = 2
        elif severity_level < 5:
            priority = 1
        else:
            priority = 0
        params = {
            'user': user_key,
            'token': Config.data['pushover']['token'],
            'title': '{}: {}'.format(Config.data['notification_prefix'], title),
            'message': message,
            'priority': priority,
        }
        if url:
            params['url'] = url
        if priority == 2:
            params['retry'] = 60
            params['expire'] = 14400 # 4 hours
        requests.post(
            'https://api.pushover.net/1/messages.json',
            params=params,
        )
        return True