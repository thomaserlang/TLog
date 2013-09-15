class Parsed(object):
    '''
    This object must be returned by all parsers.
    Ensures a standardized way of returning parsed data.
    '''

    def __init__(self, hostname, level, data, standard):
        '''

        :param hostname: str
        :param level: int
            Uses Syslog severity levels. See http://en.wikipedia.org/wiki/Syslog#Severity_levels
        :param data: dict
            You can add all the fields you like.
            Example:
                - message
                - priority
                - severity
                - facility
        :param standard: str
            The standard which were detected.
            Example: Syslog 5424
        '''
        self.hostname = hostname
        self.level = level
        self.data = data
        self.standard = standard

    def to_dict(self):
        return self.__dict__