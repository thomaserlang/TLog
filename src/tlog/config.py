import json
import os

class Config(object):
    data = {
        'debug': False,
        'admin_emails': [],
        'admin_pushover': [],
        'url': 'http://tlog.example.com',
        'database': {
            'url': 'sqlite:///tlog.db',
        },
        'sample_data': True,
        'sample_rates': [
            [50, 1],
            [1000, 2],
            [10000, 10],
            [100000, 50],
            [1000000, 300],
            [10000000, 2000],
        ],
        'max_sample_rate': 10000,
        'sample_times': [
            [3600, 1],
            [360, 10],
            [60, 60],
        ],
        'max_sample_time': 10000,
        'web': {
            'cookie_secret': '#L0YnUrNM*yet*VR4Ft4bd4$K2Beco#5',
            'port': 8001,
            'pool_size': 5,
        },
        'celery': {
            'enabled': False,
            'broker': 'amqp://guest@localhost//',
            'backend': 'amqp://guest@localhost//',
        },
        'email': {
            'enabled': False,
            'server': 'localhost',
            'port': 21,
            'use_tls': False,
            'username': '',
            'password': '',
            'from': 'tlog@example.com'
        },
        'logging': {
            'level': 'info',
            'path': None,
            'max_size': 100 * 1000 * 1000,# ~ 95 mb
            'num_backups': 10,
        },
        'elasticsearch': {
            'enabled': False,
            'url': 'http://localhost:9200/'
        },
        'heartbeat': {
            'target_ip': 'localhost',
            'target_port': 514,
            'wait_time': 1, # minutes
        },
        'pushover': {
            'enabled': False,
            'token': '',
        },
        'notification_prefix': '[TLog]',
        'receiver': {
            'port': 514,
        }
    }

    @classmethod
    def load(cls, path=None):
        if not path:
            path = os.environ.get('TLOG_CONFIG', './tlog.json')
        if not os.path.isfile(path):
            raise Exception(u'Config: "{}" could not be found.'.format(path))
        with open(path) as f:
            data = json.loads(f.read())
        for key in data:
            if key in cls.data:
                if isinstance(cls.data[key], dict):
                    cls.data[key].update(data[key])
                else:
                    cls.data[key] = data[key]