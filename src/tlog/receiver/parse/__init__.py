import syslog

def Parse(data):
    '''
    Tries to parse data with the diffrent parsers.

    :param data: str
    :returns: Parsed
    '''
    return syslog.Syslog.parse(data)