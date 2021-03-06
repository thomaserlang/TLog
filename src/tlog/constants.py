STATUS_UNRESOLVED = 0
STATUS_RESOLVED = 1
STATUS_LEVELS = (
    (STATUS_UNRESOLVED, 'Unresolved'),
    (STATUS_RESOLVED, 'Resolved'),
)

# id of the tlog user.
SYSTEM_USER = 1

MINUTE_NORMALIZATION = 15

SYSLOG_SEVERITY = (
    'Emergency',
    'Alert',
    'Critical',
    'Error',
    'Warning',
    'Notice',
    'Informational',
    'Debug',
)

SYSLOG_FACILITY = (
    'Kernel messages',
    'User-level messages',
    'Mail system',
    'System daemons',
    'Security/authroization messages',
    'Messages generated internally by syslogd',
    'Line printer subsystem',
    'Network news subsystem',
    'UUCP subsystem',
    'Clock daemon',
    'Security/authorization messages',
    'FTP daemon',
    'NTP subsystem',
    'Log audit',
    'Log alert',
    'Clock daemon',
    'Local use 0 (local0)',
    'Local use 1 (local1)',
    'Local use 2 (local2)',
    'Local use 3 (local3)',
    'Local use 4 (local4)',
    'Local use 5 (local5)',
    'Local use 6 (local6)',
    'Local use 7 (local7)',
)

LOG_GROUP_PER_PAGE = 15
SEARCH_RESULTS_PER_PAGE = 20

LOG_GROUP_ORDER_BY_FIRST_SEEN = 0
LOG_GROUP_ORDER_BY_LAST_SEEN = 1
LOG_GROUP_ORDER_BY_TIMES_SEEN = 2
LOG_GROUP_ORDER_BY_LEVEL = 3
LOG_GROUP_ORDER_BY_SCORE = 4

LOG_GROUP_ORDER_BYS = (
    'first_seen ASC',
    'last_seen DESC',
    'times_seen DESC',
    'level ASC, last_seen DESC',
    'score DESC',
)

LOG_GROUP_ORDER_BY_NAMES = (
    (LOG_GROUP_ORDER_BY_FIRST_SEEN, 'First seen'),
    (LOG_GROUP_ORDER_BY_LAST_SEEN, 'Last seen'),
    (LOG_GROUP_ORDER_BY_TIMES_SEEN, 'Times seen'),
    (LOG_GROUP_ORDER_BY_LEVEL, 'Level'),
    (LOG_GROUP_ORDER_BY_SCORE, 'Score'),
)

LOG_GROUP_ORDER_BY_DEFAULT = LOG_GROUP_ORDER_BY_LAST_SEEN

LOG_GROUP_NOTIFICATION_MINUTE_LIMIT = 30 # only send a notification if there hasnt been sent on in the last 30 minutes.
FILTER_NOTIFICATION_MINUTE_LIMIT = 30 # only send a notification if there hasnt been sent on in the last 30 minutes.

COLORS = (
    '#F0F8FF',
    '#FAEBD7',
    '#00FFFF',
    '#7FFFD4',
    '#F0FFFF',
    '#F5F5DC',
    '#FFE4C4',
    '#000000',
    '#FFEBCD',
    '#0000FF',
    '#8A2BE2',
    '#A52A2A',
    '#DEB887',
    '#5F9EA0',
    '#7FFF00',
    '#D2691E',
    '#FF7F50',
    '#6495ED',
    '#FFF8DC',
    '#DC143C',
    '#00FFFF',
    '#00008B',
    '#008B8B',
    '#B8860B',
    '#A9A9A9',
    '#006400',
    '#BDB76B',
    '#8B008B',
    '#556B2F',
    '#FF8C00',
    '#9932CC',
    '#8B0000',
    '#E9967A',
    '#8FBC8F',
    '#483D8B',
    '#2F4F4F',
    '#00CED1',
    '#9400D3',
    '#FF1493',
    '#00BFFF',
    '#696969',
    '#1E90FF',
    '#B22222',
    '#FFFAF0',
    '#228B22',
    '#FF00FF',
    '#DCDCDC',
    '#F8F8FF',
    '#FFD700',
    '#DAA520',
    '#808080',
    '#008000',
    '#ADFF2F',
    '#F0FFF0',
    '#FF69B4',
    '#CD5C5C',
    '#4B0082',
    '#FFFFF0',
    '#F0E68C',
    '#E6E6FA',
    '#FFF0F5',
    '#7CFC00',
    '#FFFACD',
    '#ADD8E6',
    '#F08080',
    '#E0FFFF',
    '#FAFAD2',
    '#D3D3D3',
    '#90EE90',
    '#FFB6C1',
    '#FFA07A',
    '#20B2AA',
    '#87CEFA',
    '#778899',
    '#B0C4DE',
    '#FFFFE0',
    '#00FF00',
    '#32CD32',
    '#FAF0E6',
    '#FF00FF',
    '#800000',
    '#66CDAA',
    '#0000CD',
    '#BA55D3',
    '#9370DB',
    '#3CB371',
    '#7B68EE',
    '#00FA9A',
    '#48D1CC',
    '#C71585',
    '#191970',
    '#F5FFFA',
    '#FFE4E1',
    '#FFE4B5',
    '#FFDEAD',
    '#000080',
    '#FDF5E6',
    '#808000',
    '#6B8E23',
    '#FFA500',
    '#FF4500',
    '#DA70D6',
    '#EEE8AA',
    '#98FB98',
    '#AFEEEE',
    '#DB7093',
    '#FFEFD5',
    '#FFDAB9',
    '#CD853F',
    '#FFC0CB',
    '#DDA0DD',
    '#B0E0E6',
    '#800080',
    '#FF0000',
    '#BC8F8F',
    '#4169E1',
    '#8B4513',
    '#FA8072',
    '#F4A460',
    '#2E8B57',
    '#FFF5EE',
    '#A0522D',
    '#C0C0C0',
    '#87CEEB',
    '#6A5ACD',
    '#708090',
    '#FFFAFA',
    '#00FF7F',
    '#4682B4',
    '#D2B48C',
    '#008080',
    '#D8BFD8',
    '#FF6347',
    '#40E0D0',
    '#EE82EE',
    '#F5DEB3',
    '#FFFFFF',
    '#F5F5F5',
    '#FFFF00',
    '#9ACD32',
)

NOTIFICATION_TYPES = (
    ('send_email', 'Email', 'Insert your email address'),
    ('send_pushover', 'Pushover', 'Insert your user key'),
)