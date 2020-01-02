#!/usr/bin/env python3
import time
import psutil
import sys

from utils import config
from utils import logger
from utils.rclone import rclone
from utils.plex import Plex

log = logger.get_root_logger()
server = None

def check_proc():
    log.debug("Checking processes...")
    procfound = False
    for proc in psutil.process_iter():
        if proc.name().startswith('rclone'):
            log.debug("%s (%s)- %s is %s",
                      proc.name(),
                      psutil.Process(proc.pid).pid,
                      psutil.Process(proc.pid).cmdline(),
                      psutil.Process(proc.pid).status()
                      )
            procfound = True

    return procfound


def enable_proc():
    log.debug("Enabling processes...")
    for proc in psutil.process_iter():
        if proc.name().startswith('rclone'):
            if psutil.Process(proc.pid).status() == 'stopped':
                log.info("%s ENABLED", proc)
                psutil.Process(proc.pid).resume()


def disable_proc():
    log.debug("Disabling processes...")
    for proc in psutil.process_iter():
        if proc.name().startswith('rclone'):
            if psutil.Process(proc.pid).status() != 'stopped':
                log.info("%s DISABLED", proc)
                psutil.Process(proc.pid).suspend()


if __name__ == "__main__":
    log.info("Initializing")
    log.info("Debug: %s", config.DEBUG)
    log.info("Validating server %r with token %r", config.SERVER_URL,
             config.SERVER_TOKEN)
    server = Plex(config.SERVER_NAME, config.SERVER_URL, config.SERVER_TOKEN)
    checkwait = config.CHECK_INTERVAL
    disabled = True
    if not server.validate():
        log.error("Could not validate server token, are you sure its correct...")
        exit(1)
    else:
        log.info("Server token was validated, so far so good.")

    check_proc()
    rclone = rclone()

    server.check_streams()

    #rclone.set_bw(700)

    while True:
        log.debug("Checking streams every %s seconds", checkwait)

        if check_proc():
            server.check_streams()
            if server.remote_bw > 0:
                setbw = int(config.BW_MAX - (server.remote_bw * config.BW_FACTOR))
                log.info("Current remote BW: %s, setting rclone BW to %s", server.remote_bw , setbw)
                rclone.set_bw(setbw)
            else:
                setbw = int(config.BW_MAX)
                log.info("Current remote BW: %s, setting rclone BW to %s", server.remote_bw , setbw)
                rclone.set_bw(config.BW_MAX)
        else:
            rclone = rclone()

        time.sleep(checkwait)
