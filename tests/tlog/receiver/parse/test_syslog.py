# coding=UTF-8
import nose
from unittest2 import TestCase
from tlog.receiver.parse.syslog import Syslog
from tlog.receiver.parse.parsed import Parsed

class test_syslog(TestCase):

    def test_parse_3164(self):
        log = '<34>Oct 11 22:14:15 mymachine su: su root failed for lonvick on /dev/pts/8'
        syslog = Syslog.parse_3164(log)
        self.assertTrue(isinstance(syslog, Parsed))
        self.assertEqual(syslog.hostname, 'mymachine')
        self.assertEqual(syslog.data['priority'], 34)
        self.assertEqual(syslog.data['facility'], 4)
        self.assertEqual(syslog.level, 2)
        self.assertEqual(syslog.data['app-name'], 'su')
        self.assertEqual(syslog.data['message'], 'su root failed for lonvick on /dev/pts/8')

    def test_parse_process_info_3164(self):
        # with app-name and procid
        message = 'su[123]: \'su root\' failed for lonvick on /dev/pts/8'
        m, data = Syslog.parse_process_info_3164(message)
        self.assertEqual('\'su root\' failed for lonvick on /dev/pts/8', m)
        self.assertEqual(data['app-name'], 'su')
        self.assertEqual(data['procid'], 123)

        # with app-name
        message = 'su: \'su root\' failed for lonvick on /dev/pts/8'
        m, data = Syslog.parse_process_info_3164(message)
        self.assertEqual('\'su root\' failed for lonvick on /dev/pts/8', m)
        self.assertEqual(data['app-name'], 'su')
        self.assertTrue('procid' not in data)

        # no app-name and procid
        message = '\'su root\' failed for: lonvick on /dev/pts/8'
        m, data = Syslog.parse_process_info_3164(message)
        self.assertEqual(message, m)
        self.assertTrue('app-name' not in data)
        self.assertTrue('procid' not in data)

        message = ':test:\'su root\' failed for: lonvick on /dev/pts/8'
        m, data = Syslog.parse_process_info_3164(message)
        self.assertEqual('test:\'su root\' failed for: lonvick on /dev/pts/8', m)
        self.assertTrue('app-name' not in data)
        self.assertTrue('procid' not in data)

    def test_parse_5424(self):
        log = '<34>1 2013-08-11T22:14:15.003Z mymachine.example.com su - ID47 [exampleSDID@32473 iut="3" eventSource="Application \\"[test\\]\\"" eventID="1011"][examplePriority@32473 class="high"] BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'
        syslog = Syslog.parse_5424(log)
        self.assertTrue(isinstance(syslog, Parsed))
        self.assertEqual(syslog.hostname, 'mymachine.example.com')
        self.assertEqual(syslog.data['priority'], 34)
        self.assertEqual(syslog.data['facility'], 4)
        self.assertEqual(syslog.level, 2)
        self.assertEqual(syslog.data['app-name'], 'su')
        self.assertTrue('procid' not in syslog.data)
        self.assertEqual(syslog.data['msgid'], 'ID47')
        self.assertEqual(syslog.data['message'], u'\'su root\' failed for lonvick on /dev/pts/8 æøå')
        self.assertTrue(u'exampleSDID@32473' in syslog.data['structured-data'])
        self.assertEqual(syslog.data['structured-data']['exampleSDID@32473']['iut'], '3')
        self.assertEqual(syslog.data['structured-data']['exampleSDID@32473']['eventSource'], 'Application "[test]"')
        self.assertEqual(syslog.data['structured-data']['exampleSDID@32473']['eventID'], '1011')
        self.assertTrue(u'examplePriority@32473' in syslog.data['structured-data'])
        self.assertEqual(syslog.data['structured-data']['examplePriority@32473']['class'], 'high')

        log = '<34>1 2013-08-11T22:14:15.003Z mymachine.example.com - - - - BOM\'su root\' failed for lonvick on /dev/pts/8 æøå'
        syslog = Syslog.parse_5424(log)
        self.assertTrue(isinstance(syslog, Parsed))
        self.assertEqual(syslog.hostname, 'mymachine.example.com')
        self.assertEqual(syslog.data['priority'], 34)
        self.assertEqual(syslog.data['facility'], 4)
        self.assertEqual(syslog.level, 2)
        self.assertTrue('app-name' not in syslog.data)
        self.assertTrue('procid' not in syslog.data)
        self.assertTrue('msgid' not in syslog.data)
        self.assertEqual(syslog.data['message'], u'\'su root\' failed for lonvick on /dev/pts/8 æøå')
        self.assertTrue('structured-data' not in syslog.data)

    def test_parse(self):
        log = '<34>Oct 11 22:14:15 mymachine su: su root failed for lonvick on /dev/pts/8'
        syslog = Syslog.parse(log)
        self.assertTrue(isinstance(syslog, Parsed))
        self.assertEqual(syslog.standard, 'Syslog 3164')

        log = '<34>1 2013-08-11T22:14:15.003Z mymachine.example.com su - ID47 - BOM\'su root\' failed for lonvick on /dev/pts/8'
        syslog = Syslog.parse(log)
        self.assertTrue(isinstance(syslog, Parsed))
        self.assertEqual(syslog.standard, 'Syslog 5424')

    def test_parse_structured_data(self):
        parsed = Syslog.parse_structured_data('[exampleSDID@32473 iut="3" eventSource="Application \\"[test\\]\\"" eventID="1011"][examplePriority@32473 class="high"]')

        self.assertTrue(u'exampleSDID@32473' in parsed)
        self.assertEqual(parsed['exampleSDID@32473']['iut'], '3')
        self.assertEqual(parsed['exampleSDID@32473']['eventSource'], 'Application "[test]"')
        self.assertEqual(parsed['exampleSDID@32473']['eventID'], '1011')
        
        self.assertTrue(u'examplePriority@32473' in parsed)
        self.assertEqual(parsed['examplePriority@32473']['class'], 'high')

        parsed = Syslog.parse_structured_data('[iut="3" eventSource="Application \\"[test\\]\\"" eventID="1011"]')
        self.assertEqual(parsed['iut'], '3')
        self.assertEqual(parsed['eventSource'], 'Application "[test]"')
        self.assertEqual(parsed['eventID'], '1011')

if __name__ == '__main__':
    nose.run(defaultTest=__name__)