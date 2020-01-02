import json
import requests
import time
import psutil
from urllib.parse import quote_plus 
from datetime import datetime as dt, timedelta as td
from utils import config
from utils import logger


log = logger.get_logger(__name__)


class rclone(object):
    def __init__(self):
        self._session = requests.Session()
        self.host = 'http://localhost:5572/'
        #self.get_pid()
        self.bw_setlimit = {
            "time": dt.now(),
            "rate": 0
        }
        self.bw_confirmed_limit = {
            "time": dt.now(),
            "rate": 0
        }
        
    def get_pid(self):
        url = self.host + 'core/pid'
        r = self._session.post(url).json()
        self.pid = r['pid']
        log.debug(r)

    def get_bw_limit(self):
        url = self.host + 'core/bwlimit'
        r = self._session.post(url).json()
        log.debug(r)
        if self.bw_confirmed_limit['rate'] != r['bytesPerSecond']:
            log.debug("Updating stored limit via get_bw_limit, new limit %s", r['bytesPerSecond'])
            self.bw_confirmed_limit['rate'] = r['bytesPerSecond']
            self.bw_confirmed_limit['time'] = dt.now()
    
    def set_bw(self, rate):
        self.get_bw_limit()
        updatetime = dt.now()
        if rate < config.BW_FLOOR:
            log.info("Limit would be below BW floor of %s, setting to BW floor.", config.BW_FLOOR)
            setrate = config.BW_FLOOR
        else:
            setrate = rate
        payload = {
            'rate': setrate
        }

        if setrate == self.bw_setlimit['rate'] and self.bw_setlimit['time'] == self.bw_confirmed_limit['time']:
            log.debug("No change to rate, already set.")
            return

        url = self.host + 'core/bwlimit'
        r = self._session.post(url, data = payload).json()
        log.debug("Setting rate to %s, response %s", setrate, r)
        self.bw_setlimit['rate'] = setrate
        self.bw_setlimit['time'] = updatetime
        self.bw_confirmed_limit['rate'] = r['bytesPerSecond']
        self.bw_confirmed_limit['time'] = updatetime
