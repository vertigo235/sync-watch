from decouple import config, Csv

DEBUG = config('DEBUG', True, cast=bool)
SERVER_URL = config('SERVER_URL')
SERVER_TOKEN = config('SERVER_TOKEN')
SERVER_NAME = config('SERVER_NAME')
CHECK_INTERVAL = config('CHECK_INTERVAL', 60, cast=int)
LOGFILE = config('LOGFILE','/config/syncwatch/status.log')
WHITELISTED_USERS = config('WHITELISTED_USERS', [], cast=Csv())
