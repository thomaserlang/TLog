import re
import logging
import tlog.base.filter

class Filter_checker(object):

    '''
    Use this class to check that a filter matches a parsed message.

    Example:

        parsed = tlog.receiver.parse.parsed.Parsed(
            hostname='te-pc', 
            level=0, 
            data={
                "message": "Some test message",
            },
            standard='Test standard',
        )

        filter_ = tlog.base.filter.Filter(
            id_=0,
            version=1,
            name='Test filter',
            data={
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
        )

        Filter_checker.check(filter_, parsed)
        >> True

    '''

    compiled_regexes = {}

    @classmethod
    def check(cls, filter_, parsed):
        '''
        In `filter_` we have "match" and "notmatch" to check against the `parsed` object.
        If both "match" and "notmatch" is specified, then we have to make sure that
        "match" returns true and "notmatch" return false before the filter is marked as a match.

        :param filter_: tlog.base.filter.Filter
        :param parsed: tlog.receiver.parse.parsed.Parsed
        :returns: boolean
        '''
        match = filter_.data.get('match', None)
        notmatch = filter_.data.get('notmatch', None)
        if match or notmatch:
            parsed_dict = parsed.to_dict()
            if match and notmatch:
                match = cls._check(match, parsed_dict)
                notmatch = cls._check(notmatch, parsed_dict)
                return ((match == True) and (notmatch == False))
            elif match:
                return cls._check(match, parsed_dict)
            elif notmatch:
                return cls._check(notmatch, parsed_dict) == False
        return False

    @classmethod
    def _check(cls, match_filter, value):
        '''
        :param match_filter: dict
            {
                "field": ["regular expression"]
                "field2": {
                    "subfield2": ["regular expression"]
                }
            }
        :param value: dict
        :returns: boolean
        '''
        for f in match_filter:
            if isinstance(match_filter[f], dict):
                v = value.get(f, None)
                if v and isinstance(v, dict):
                    if not cls._check(match_filter[f], v):
                        return False
                else:
                    return False
            else:
                v = unicode(value.get(f, None))
                if not v:
                    return False
                if not cls._validate(match_filter[f], v):
                    return False
        if match_filter:
            return True
        return False

    @classmethod
    def _validate(cls, res, value):
        '''
        Checks if `value` matches any of the regular expressions in `res`.
        Returns true if any of the regular expressions is a match.

        All regular expressions are compiled and stored in `cls.compiled_regexes` as a local compile cache.

        :param res: list of str (Regular expressions)
        :param value: str
        :returns: boolean
        '''
        if not isinstance(res, list):
            raise Exception('`res` must be a list')
        for re_str in res:
            re_compiled = cls.compiled_regexes.get(re_str, None)
            if not re_compiled:
                re_compiled = re.compile(re_str, re.IGNORECASE)
                cls.compiled_regexes[re_str] = re_compiled
            if re_compiled.match(value):
                return True
        return False

class Filters_checker(object):

    '''
    Use this class to retrieve the filters that matches the parsed message.
    '''

    @classmethod
    def check(cls, filters, parsed):
        '''
        Checks `parsed` message against `filters`.
        Returns a list of those filters that matched.

        :param filters: list of tlog.base.filter.Filter
        :param parsed: tlog.receiver.parse.parsed.Parsed
        :returns: list of tlog.base.filter.Filter
        '''
        matched_filters = []
        for filter_ in filters:
            if isinstance(filter_.data, list):
                fs = []
                for f in filter_.data:
                    fs.append(
                        tlog.base.filter.Filter(
                            id_=filter_.id,
                            version=filter_.version,
                            name=f.get('name', filter_.name),
                            data=f,
                            data_yaml='',
                        )
                    )
                if fs: 
                    matched_filters.extend(cls.check(fs, parsed))
            else:
                try:
                    if Filter_checker.check(filter_, parsed):
                        matched_filters.append(filter_)
                except Exception:
                    logging.exception(u'Failed to validate the message against filter: {}. Probably a syntax error.'.format(filter_.name))
        return matched_filters