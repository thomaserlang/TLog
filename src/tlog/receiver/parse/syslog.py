import logging
import re
import dateutil.parser
from tlog.receiver.parse.parsed import Parsed

class Syslog(object):
    '''
    Class for parsing different syslog standards.

    Parse a syslog message:

        Syslog.parse('some syslog').
    
    Returns none if the log format is not supported. 
    
    Supported standards:

        * RFC 3164
        * RFC 5424

    '''
                            #    PRI           TIMESTAMP          HOST  MESSAGE  
    regex_3164 = re.compile('^<([0-9]+)>([a-z ]+ [0-9]+ [0-9:]+) ([^ ]+) (.*)$', re.IGNORECASE)
                            #    PRI    VERSION   TIME    HOST      APP       PROCID     MSGID    STRUC-DATA  MESSAGE
    regex_5424 = re.compile('^<([0-9]+)>([0-9]+) ([^ ]+) ([^ ]+) ([^- ]+|-) ([^- ]+|-) ([^- ]+|-) (\[.*\]|-) (.*)$', re.IGNORECASE)

    @classmethod
    def parse_message(cls, message):
        '''
        Removes BOM from the message. 
        BOM indicates that the message is encoded with utf-8.

        :param message: str
        :returns: str
        '''
        if message[:3] == 'BOM':
            if isinstance(message, unicode):
                return message[3:]
            return message[3:].decode('utf-8')
        return message

    @classmethod 
    def parse_process_info_3164(cls, message):
        '''
        Retrunes process info from a message and the message, where the process info has been removed.

        Example:
            
            su[123]: 'su root' failed for lonvick on /dev/pts/8

        :param message: str
        :returns: (str, dict)
            str:
                'su root' failed for lonvick on /dev/pts/8
            dict:
                {
                    'app-name': 'su',
                    'procid': 123
                }
        '''
        i = 0
        value = ''
        data = {}
        prev_s = ''
        if message[:1] == ':':
            return (message[1:], data)
        for s in message:
            i += 1
            if s == ' ' and prev_s == ':':
                if 'app-name' in data:
                    return (message[i:], data)
            elif s == ' ':
                return (message, data) 
            elif s in ('[', ':'):
                if 'app-name' not in data:
                    data['app-name'] = value 
                    value = ''
                prev_s = s
                continue
            elif s == ']':
                data['procid'] = int(value)
                continue
            value = value + s
            prev_s = s
        return (message, data)

    @classmethod
    def parse_structured_data(cls, structured_data):
        '''
        Parses a structured-data as specified in: http://tools.ietf.org/html/rfc5424#section-6.3

        Example:

            [exampleSDID@32473 iut="3" eventSource="Application \\"[test\\]\\"" eventID="1011"][examplePriority@32473 class="high"]

        :param structured_data: str
            http://tools.ietf.org/html/rfc5424#section-6.3
        :returns: dict
            {
                'exampleSDID@32473': {
                    'iut': '3',
                    'eventSource': 'Application "[test]"',
                    'eventID': '1011'
                },
                'examplePriority@32473': {
                    'class': 'high'
                }
            }
        '''
        def remove_escaped(value):
            # http://tools.ietf.org/html/rfc5424#section-6.3.3
            value = value.replace(u'\\"', u'"')
            value = value.replace(u'\\]', ']')
            value = value.replace(u'\\\\', '\\')            
            return value

        if isinstance(structured_data, str):
            structured_data = structured_data.decode('utf-8')
        parsed = {}
        d = parsed
        key = u''
        find_key = True
        find_field = False
        value = u''
        in_string = False
        prev_s = u''
        for s in structured_data:
            if not in_string:
                if s == u'[':
                    find_key = True
                    find_field = False
                    d = parsed
                    continue
                if s in (u' ', u']'): # key found
                    if not key:
                        continue
                    parsed[key] = {}
                    d = parsed[key]
                    find_field = True
                    key = ''
                    continue
                if s == u'=':# key found and value start
                    find_field = False
                    in_string = False
                    continue
            if s == u'"' and prev_s <> u'\\':
                if not in_string:
                    in_string = True
                    continue
                # value found
                d[key] = remove_escaped(value)
                value = ''
                key = ''
                find_field = True
                in_string = False
                continue
            if not in_string:
                key = key + s
            else:
                value = value + s
            prev_s = s
        return parsed


    @classmethod
    def parse_3164(cls, log):
        '''
        :returns: ``Parsed``
        '''
        match = cls.regex_3164.match(log)
        if match:
            pri = int(match.group(1))
            severity = pri % 8
            message, process_info = cls.parse_process_info_3164(match.group(4))
            data = {
                'message': cls.parse_message(message),
                'priority': pri,
                'facility': pri / 8,
                'severity': severity,
                'timestamp': dateutil.parser.parse(match.group(2)),
            }
            data.update(process_info)
            return Parsed(
                hostname=match.group(3), 
                level=severity,
                data=data,
                standard=u'Syslog 3164',
            )
        return None

    @classmethod
    def parse_5424(cls, log):
        '''
        :returns: ``Parsed``
        '''
        match = cls.regex_5424.match(log)
        if match:
            pri = int(match.group(1))
            severity = pri % 8
            data = {
                'message': cls.parse_message(match.group(9)),
                'priority': pri,
                'facility': pri / 8,
                'severity': severity,                    
                'timestamp': dateutil.parser.parse(match.group(3)),
            }
            if match.group(5) <> '-':
                data['app-name'] = match.group(5)
            if match.group(6) <> '-':
                data['procid'] = match.group(6)
            if match.group(7) <> '-':
                data['msgid'] = match.group(7)
            if match.group(8) <> '-':
                data['structured-data'] = cls.parse_structured_data(match.group(8))
            return Parsed(
                hostname=match.group(4),
                level=severity,
                data=data,
                standard=u'Syslog 5424',
            )
        return None

    @classmethod
    def parse(cls, log):
        '''
        Tries the different log standards.
        Returns none if the log format is not supported. 
        
        :returns: Parsed
        '''
        s_3164 = cls.parse_3164(log)
        if s_3164:
            return s_3164
        s_5424 = cls.parse_5424(log)
        if s_5424:
            return s_5424
        return None