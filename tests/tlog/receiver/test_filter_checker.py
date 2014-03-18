import nose
import yaml
from unittest2 import TestCase
from tlog.base.filter import Filter
from tlog.receiver.filter_checker import Filter_checker, Filters_checker
from tlog.receiver.parse.parsed import Parsed
from tlog.receiver.store import Store

class test_filter_checker(TestCase):
    
    def test_check(self):
        parsed = Parsed(
            hostname='te-pc', 
            level=0, 
            data={
                "message": "Some test message",
            },
            standard='Test standard',
        )
        filter_ = Filter(
            id_=0,
            version=1,
            name='test',
            data={'store': True},
            data_yaml='store: true',
        )

        filter_.data = {
            'match': {
                'message': '^[a-zA-Z ]+$',
            }
        }
        self.assertTrue(Filter_checker.check(filter_, parsed))

        # check that we do not accidentally remove the `data` field
        # in th parsed message when validating it against a filter.
        store = Store(parsed, [filter_])
        self.assertTrue(isinstance(store, Store))

        filter_.data = {
            'match': {
                'hostname': [
                    'something wrong',
                ],
                'message': [
                    '^[a-zA-Z ]+$'
                ],
            }
        }
        self.assertFalse(Filter_checker.check(filter_, parsed))

        filter_.data = {
            'match': {
                'level': [
                    '[0-9]+'
                ]
            }
        }
        self.assertTrue(Filter_checker.check(filter_, parsed))


        filter_.data = {
            'match': {
                'level': [
                    '[5-6]+'
                ]
            }
        }
        self.assertFalse(Filter_checker.check(filter_, parsed))

        filter_.data = {
            'match': {
                'hostname': [
                    'te-pc',
                ],
                'data': {
                    'message': [
                        '^[a-zA-Z ]+$'
                    ],
                }
            },
            'notmatch': {
                'hostname': [
                    'te-pc',
                ]
            }
        }
        self.assertFalse(Filter_checker.check(filter_, parsed))

        filter_.data = {
            'match': {
                'level': [
                    '[0-9]+'
                ]
            },
            'notmatch': {
                'hostname': [
                    'te-pc',
                ]
            }
        }
        self.assertFalse(Filter_checker.check(filter_, parsed))

        filter_.data = {
            'match': {
                'level': [
                    '[0-9]+'
                ]
            },
            'notmatch': {
                'hostname': [
                    'kurtkurtsen',
                ]
            }
        }
        self.assertTrue(Filter_checker.check(filter_, parsed))

        filter_.data = {
            'notmatch': {
                'hostname': [
                    'kurtkurtsen',
                ]
            }
        }
        self.assertTrue(Filter_checker.check(filter_, parsed))

        filter_.data = {
            'notmatch': {
                'level': [
                    '[0-9]+',
                ]
            }
        }
        self.assertFalse(Filter_checker.check(filter_, parsed))


class test_filters_checker(TestCase):

    def test_check(self):
        parsed = Parsed(
            hostname='te-pc', 
            level=0, 
            data={
                "message": "Some test message",
            },
            standard='Test standard',
        )
        data = [
            {
                'name': 'test filter 1',
                'match': {
                    'hostname': [
                        'te-pc',
                    ],
                    'message': [
                        '^[a-zA-Z ]+$'
                    ],
                }
            },
            {
                'name': 'test filter 2',
                'match': {
                    'hostname': [
                        'te-pc',
                    ],
                    'message': [
                        '^[a-zA-Z ]+$'
                    ],
                }
            }
        ]
        filter1 = Filter(
            id_=1,
            version=1,
            name='test',
            data_yaml=yaml.safe_dump(data),
            data=data,
        )
        data = {
            'match': {
                'hostname': [
                    'something wrong',
                ],
                'message': [
                    '^[a-zA-Z ]+$'
                ],
            }
        }
        filter2 = Filter(
            id_=2,
            version=1,
            name='test',
            data=data,
            data_yaml=yaml.safe_dump(data),
        )
        filters = [filter1, filter2]
        filter_matches = Filters_checker.check(filters, parsed)
        self.assertEqual(len(filter_matches), 2)
        self.assertEqual(filter_matches[0].id, filter1.id)        
        self.assertEqual(filter_matches[1].id, filter1.id)

if __name__ == '__main__':
    nose.run(defaultTest=__name__)