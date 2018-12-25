import logging
import os
from logging.handlers import RotatingFileHandler
from utils import config

# Setup logging
log_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)-10s - %(name)-15s -  %(funcName)-25s- %(message)s')

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
file_path = config.LOGFILE

rootLogger = logging.getLogger('sync_watch')

# Console logging
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(log_formatter)
rootLogger.addHandler(console_handler)

# Rotating Log Files
file_handler = RotatingFileHandler(file_path, maxBytes=1024 * 1024 * 1, backupCount=2)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)
rootLogger.addHandler(file_handler)

rootLogger.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)


def get_root_logger():
    return rootLogger


def get_logger(name):
    logger = rootLogger.getChild(name)
    logger.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)
    return logger
