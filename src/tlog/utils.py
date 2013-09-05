import base64
import time
import os
import json
import datetime
from tlog.constants import MINUTE_NORMALIZATION

def random_key():
    return base64.b64encode('{}-{}'.format(
            os.urandom(16),
            time.time()
        )
    )

def class_to_dict(obj):
    if hasattr(obj, 'to_json'):
        return obj.to_json()
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat('T')+'Z'
    else:
        raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))

class JsonEncoder(json.JSONEncoder):
    def default(self, value):
        """Convert more Python data types to ES-understandable JSON."""
        iso = _iso_datetime(value)
        if iso:
            return iso
        if isinstance(value, set):
            return list(value)
        if hasattr(value, 'to_json'):
            return value.to_json()
        return super(JsonEncoder, self).default(value)

def _iso_datetime(value):
    """
    If value appears to be something datetime-like, return it in ISO format.

    Otherwise, return None.
    """
    if hasattr(value, 'strftime'):
        if hasattr(value, 'hour'):
            return value.isoformat()
        else:
            return '%sT00:00:00' % value.isoformat()

def json_dumps(data):
    '''
    Turns a dict into json string.

    :param data: dict
    :returns: str
    '''
    return json.dumps(data, default=class_to_dict)

def mean(values):
    return sum(values) / len(values)

def median(values):
    values = sorted(values)
    size = len(values)
    if size % 2 == 1:
        return values[int((size - 1) / 2)]
    return (values[int(size / 2 - 1)] + values[int(size / 2)]) / 2

def mad(values, K=1.4826):
    # http://en.wikipedia.org/wiki/Median_absolute_deviation
    med = median(values)
    return K * median([abs(val - med) for val in values])

def normalize_datetime(datetime, minutes=MINUTE_NORMALIZATION):
    minutes = (datetime.minute - (datetime.minute % minutes))
    normalized_datetime = datetime.replace(second=0, microsecond=0, minute=minutes)
    return normalized_datetime