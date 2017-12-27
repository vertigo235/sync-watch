#!/usr/bin/env python2.7
import time
import psutil

from utils import config
from utils import logger
from utils.plex import Plex

log = logger.get_root_logger()
server = None


def remote_stream_check(stream):
    if not stream.ip_address.startswith("192.168.1"):
        return True
    else:
        return False


def check_streams():
    log.debug("Retrieving active stream(s) for server: %s", server.name)
    streams = server.get_streams()

    if streams is None:
        log.error("There was an error while retrieving the active streams...")
        return
    elif not streams:
        log.debug("There's currently no streams to check")
        return
    else:
        log.debug("Checking %d stream(s)", len(streams))

    for stream in streams:
        log.debug("Checking stream: %s", stream)
        if stream.ip_address.startswith("192.168.1"):
            log.debug("Local stream... %s" % stream.ip_address)
            continue
        elif stream.state == 'paused':
            log.debug("Paused stream... %s", stream.ip_address)
            continue
        else:
            log.debug("Remote stream detected! %s", stream.ip_address)
            return True

    log.debug("Done checking streams...")
    return False


def check_proc():
    log.debug("Checking processes...")
    procfound = False
    for proc in psutil.process_iter():
        if proc.name().find('rclone') >= 0:
            log.debug("%s (%s)- %s is %s",
                      proc.name(),
                      psutil.Process(proc.pid).pid,
                      psutil.Process(proc.pid).cmdline(),
                      psutil.Process(proc.pid).status()
                      )
            procfound = True

    return procfound


def test_proc():
    for proc in psutil.process_iter():
        # log.info("%s %s",proc.name().find('rclone'),proc)
        if proc.name().startswith('rclone'):
            log.info("Found it! %s" % proc)


def enable_proc():
    log.debug("Enabling processes...")
    for proc in psutil.process_iter():
        if proc.name().find('rclone') >= 0:
            if psutil.Process(proc.pid).status() == 'stopped':
                log.info("%s ENABLED", proc)
                psutil.Process(proc.pid).resume()


def disable_proc():
    log.debug("Disabling processes...")
    for proc in psutil.process_iter():
        if proc.name().find('rclone') >= 0:
            if psutil.Process(proc.pid).status() != 'stopped':
                log.info("%s DISABLED", proc)
                psutil.Process(proc.pid).suspend()


if __name__ == "__main__":
    log.info("Initializing")
    log.info("Validating server %r with token %r", config.SERVER_URL,
             config.SERVER_TOKEN)
    server = Plex(config.SERVER_NAME, config.SERVER_URL, config.SERVER_TOKEN)
    checkwait = 10
    disabled = True
    if not server.validate():
        log.error("Could not validate server token, are you sure its correct...")
        exit(1)
    else:
        log.info("Server token was validated, proceeding to uphold the law!")

    while True:
        log.debug("Checking streams in %s seconds", config.CHECK_INTERVAL)

        # test_proc()

        if check_proc():
            log.debug("Found a process, doing that thing")
            if check_streams():
                disable_proc()
                checkwait = 5
                disabled = True
                log.debug("Stream found, waiting for %s", checkwait)
            else:
                if disabled:
                    enable_proc()
                disabled = False
                checkwait = 5
                log.debug("No remote found, waiting for %s", checkwait)
        else:
            log.debug("No processes found... waiting for %s", checkwait)

        time.sleep(checkwait)
