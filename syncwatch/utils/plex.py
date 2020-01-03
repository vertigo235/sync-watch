import logging
import json
import platform
from urllib.parse import urljoin
from uuid import getnode

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from utils import logger

log = logger.get_logger(__name__)
logging.getLogger("requests").setLevel(logging.WARNING)

class Plex(object):
    def __init__(self, name, url, token):
        self.name = name
        self.url = url
        self.token = token
        self.remote_bw = 0
        self.remote_stream = False
        self.headers = {
            'X-Plex-Token': self.token,
            'Accept': 'application/json',
            'X-Plex-Provides': 'controller',
            'X-Plex-Platform': platform.uname()[0],
            'X-Plex-Platform-Version': platform.uname()[2],
            'X-Plex-Product': 'sync_watch',
            'X-Plex-Version': '0.9.5',
            'X-Plex-Device': platform.platform(),
            'X-Plex-Client-Identifier': str(hex(getnode()))
        }

    def validate(self):
        request_url = urljoin(self.url, 'status/sessions')
        headers = self.headers

        try:
            r = requests.get(request_url, headers=headers, verify=False)
            if r.status_code == 200 and r.headers['Content-Type'] == 'application/json':
                #log.debug("Server responded with status_code=%r, content: %r", r.status_code, r.json())
                return True
            else:
                log.error("Server responded with status_code=%r, content: %r", r.status_code, r.content)
                return False
        except:
            log.exception("Exception validating server token=%r, url=%r: ", self.token, self.url)
            return False

    def check_streams(self):
        streams = self.get_streams()
        remotestream = False
        bw = 0

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
            if stream.stream_location == "lan":
                log.debug("Local stream... %s", stream.ip_address)
            elif stream.state == 'paused':
                log.debug("Paused stream... %s", stream.ip_address)
            else:
                log.debug("Remote stream detected! %s", stream.ip_address)
                bw = bw + stream.stream_KBs
                remotestream = True

        self.remote_bw = bw
        self.remote_stream = remotestream
        log.debug("Total Remote BW: %s", self.remote_bw)
        log.debug("Done checking streams...")
        return remotestream    

    def get_streams(self):
        request_url = urljoin(self.url, 'status/sessions')
        headers = self.headers

        try:
            r = requests.get(request_url, headers=headers, verify=False)
            if r.status_code == 200 and r.headers['Content-Type'] == 'application/json':
                result = r.json()
                #log.debug("Server responded with status_code=%r, content: %r", r.status_code, r.content)

                if 'MediaContainer' not in result:
                    log.error("Failed to retrieve streams from server %r", self.name)
                    return None
                elif 'Metadata' not in result['MediaContainer']:
                    log.debug("There were no streams to check for server %r", self.name)
                    return []

                streams = []
                for stream in result['MediaContainer']['Metadata']:
                    #log.debug("Stream: %r", json.dumps(stream))
                    streams.append(PlexStream(stream))
                return streams

            else:
                log.error(
                    "Server url or token was invalid, token=%r, request_url=%r, status_code=%r, content: %r",
                    self.token, request_url, r.status_code, r.content)
                return None
        except:
            log.exception("Exception retrieving streams from request_url=%r, token=%r: ", request_url, self.token)
            return None

# helper classes (parsing responses etc...)
class PlexStream(object):
    def __init__(self, stream):
        #log.info(stream['Media']['stream'])
        
        if 'User' in stream:
            self.user = stream['User']['title']
        else:
            self.user = 'Unknown'
            
        if 'Player' in stream:
            self.player = stream['Player']['product']
            self.ip = stream['Player']['remotePublicAddress']
        else:
            self.player = 'Unknown'
            self.ip = 'Unknown'

        if 'Session' in stream:
            self.session_id = stream['Session']['id']
            self.stream_location = stream['Session']['location']
            self.stream_bandwidth = stream['Session']['bandwidth']
            self.stream_KBs = self.stream_bandwidth / 7.812
        else:
            self.session_id = 'Unknown'
            self.stream_location = 'Unknown'
            
        if 'Player' in stream:
            self.state = stream['Player']['state']
        else:
            self.state = 'Unknown'
        
        if 'Player' in stream:
            self.ip_address = stream['Player']['address']
        else:
            self.ip_address = 'Unknown'
            
        if 'Media' in stream and 'Part' in stream['Media'][0] and 'decision' in stream['Media'][0]['Part'][0]:
            self.type = stream['Media'][0]['Part'][0]['decision']
        else:
            self.type = 'Unknown'
            
        if self.type == 'transcode':
            if 'TranscodeSession' in stream:
                self.video_decision = stream['TranscodeSession']['videoDecision']
                self.audio_decision = stream['TranscodeSession']['audioDecision']
            else:
                self.video_decision = 'Unknown'
                self.audio_decision = 'Unknown'
        else:
            self.video_decision = 'directplay'
            self.audio_decision = 'directplay'

        if 'title' not in stream or 'type' not in stream:
            self.title = 'Unknown'
        else:
            self.title = stream['title']

    def __str__(self):
        if self.type == 'transcode':
            transcode_type = "("
            if self.video_decision == 'transcode':
                transcode_type += "video"
            if self.audio_decision == 'transcode':
                if 'video' in transcode_type:
                    transcode_type += " & "
                transcode_type += "audio"
            transcode_type += ")"
            stream_type = "transcode {}".format(transcode_type)
        else:
            stream_type = self.type

        return u"{user} ({ip_address})/({ip}) location: {location} is playing {media} using {player}. " \
               "Stream state: {state} | bw: {bandwidth} ({KBs} KB/s), type: {type}. Session key: {session}".format(user=self.user,
                                                                                    media=self.title,
                                                                                    player=self.player,
                                                                                    state=self.state,
                                                                                    bandwidth=self.stream_bandwidth,
                                                                                    KBs=self.stream_KBs,
                                                                                    type=self.type,
                                                                                    ip_address=self.ip_address,
                                                                                    ip=self.ip,
                                                                                    location=self.stream_location,
                                                                                    session=self.session_id)

    def __getattr__(self, item):

        try:
            return self.__getattribute__(item)
        except AttributeError:
            pass

        # Default behaviour
        return 'Unknown'
