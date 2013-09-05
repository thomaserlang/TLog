import nose
from unittest import TestCase
from tlog.receiver.parse import Parse
from tlog.receiver.parse.parsed import Parsed

class test_parse(TestCase):

    def test_parse(self):
        data = '<34>Oct 11 22:14:15 mymachine.example.com su - ID47 - BOM\'su root\' failed for lonvick on /dev/pts/8'
        parsed = Parse(data)
        self.assertTrue(isinstance(parsed, Parsed))
        self.assertEqual(parsed.standard, 'Syslog 3164')

        data = '<34>1 2013-08-11T22:14:15.003Z mymachine.example.com su - ID47 - BOM\'su root\' failed for lonvick on /dev/pts/8'
        parsed = Parse(data)
        self.assertTrue(isinstance(parsed, Parsed))
        self.assertEqual(parsed.standard, 'Syslog 5424')

if __name__ == '__main__':
    nose.run(defaultTest=__name__)