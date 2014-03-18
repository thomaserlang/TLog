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
        '''
        To make it easier to write filters the dynamic field `data`'s 
        content will be merged with the other data elements without 
        having to remember which fields is in `data` and which is not.

        Example:

            ```python
            Parsed(
                hostname='te-pc', 
                level=0, 
                data={
                    "message": "Some test message",
                },
                standard='Test standard',
            )
            ```
            To write a filter that matches the above object will write it like this:
            
            ```python
            {
                'hostname': [
                    'te-pc'
                ],
                'match': {
                    'message': [
                        '^[a-zA-Z ]+$'
                    ],
                }
            }
            ```

            See how we can skip the data field? Pretty sweet.

        '''
        d = self.__dict__
        if 'data' in d:
            data = d.pop('data')
            d.update(data)
        return d