import json
import requests
import time
import psutil
from urllib.parse import quote_plus 
from utils import config
from utils import logger

log = logger.get_logger(__name__)


class rclone(object):
    def __init__(self):
        self._session = requests.Session()
        self.host = 'http://localhost:5572/'
        self.get_bw_limit()

    def get_bw_limit(self):
        url = self.host + 'core/bwlimit'
        r = self._session.post(url).json()
        log.debug(r)