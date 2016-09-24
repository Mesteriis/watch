"""
Play a URL on the Apple TV

Spec reference:
https://nto.github.io/AirPlay.html
"""

from __future__ import print_function

import requests
import socket
import time
import uuid

from .bar import TimedBar


USER_AGENT = 'MediaControl/1.0'


def server_info(apple_tv):
    response = requests.get('http://{}:7000/server-info'.format(apple_tv))
    return response.content


def position(apple_tv):
    response = requests.get('http://{}:7000/scrub'.format(apple_tv))
    lines = response.content.splitlines()
    position = {l.split(b': ')[0]: float(l.split(b': ')[1]) for l in lines}

    try:
        return position[b'position'] / position[b'duration'], int(position[b'position']), int(position[b'duration'])
    except ZeroDivisionError:
        return None, None, None
    except KeyError:
        return None, None, None


def convert_timestamp_to_seconds(seconds=0, minutes=0, hours=0):
    total = int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)
    return total


def play(url, apple_tv, start=0.0003):
    """
    Start can take one of three different formats:
        - None > start from the start of the video (well, moments after the start)
        - 0.33 > a float indicating the percentage through the video
        - hh:mm:ss > a timestamp indicating the time to jump to
            - this required the video to _start playing_ then make the jump
    """
    jump_to = None
    if not start:
        start = 0.0001
    elif isinstance(start, str):
        if ':' in start:
            jump_to = convert_timestamp_to_seconds(*reversed(start.split(':')))
            start = 0.0001
        elif '.' in start:
            start = float(start)

    data = 'Content-Location: {}\nStart-Position:{:.4f}\n'.format(url, start)

    session_id = uuid.uuid4().hex

    # ensure that `response.content` is never read, since that will kill the connection
    stream = requests.post('http://{}:7000/play'.format(apple_tv), data=data, stream=True, headers={
        'Content-Type': 'text/parameters',
        'User-Agent': USER_AGENT,
        'X-Apple-Session-ID': session_id
    })

    # get the socket for the connection, we'll be sending some junk to that later
    stream_socket = socket.fromfd(stream.raw.fileno(), socket.AF_INET, socket.SOCK_STREAM)

    bar = None
    previous = 0

    has_played = False
    has_jumped = False

    junk_timer = time.time()

    while 1:
        percentage, pos, duration = position(apple_tv)

        if percentage:
            has_played = True

            # send a "junk" /scrub request to to socket every 10 seconds or so
            if time.time() - junk_timer > 10:
                message = "GET /scrub HTTP/1.1\n\n"
                stream_socket.send(message)
                junk_timer = time.time()

            # scrub to the desired spot in the video if we need to
            if not has_jumped and jump_to:
                requests.post('http://{}:7000/scrub?position={}'.format(apple_tv, jump_to))
                has_jumped = True

            if not bar:
                bar = TimedBar('Playing', max=duration)

            while pos > previous:
                bar.next()
                previous = previous + 1

        elif has_played:
            stream.close()
            return
