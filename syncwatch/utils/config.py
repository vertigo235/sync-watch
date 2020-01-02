import os
from decouple import config

DEBUG = config('DEBUG', False, cast=bool)
SERVER_URL = config('SERVER_URL')
SERVER_TOKEN = config('SERVER_TOKEN')
SERVER_NAME = config('SERVER_NAME')
CHECK_INTERVAL = config('CHECK_INTERVAL', 5, cast=int)
BW_MAX = config('BW_MAX', 1750, cast=int)
BW_FLOOR = config('BW_FLOOR', 100, cast=int)
BW_FACTOR = config('BW_FACTOR', 1.1, cast=float)
if os.environ.get('DOCKER') == 'YES':
    LOGFILE = config('LOGFILE', '/config/status.log')
else:
    LOGFILE = config('LOGFILE', os.path.join( os.path.dirname(os.path.dirname(__file__)), 'status.log'))


