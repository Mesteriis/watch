#!/usr/bin/env python

"""Watch 1.0.0

Stream things to your Apple TV from the CLI.

Usage:
    watch <video_url> [--verbose] [--apple-tv=<atv>] [--start=<start>]

Options:
    --start=<start>       Time (hh:mm:ss) or percentage complete (0.xx) to start through the stream [default: 0.0]
    --apple-tv=<atv>      Override the APPLE_TV_IP environment variable
    --verbose             Enable detailed logging for debugging

Examples:
    - watch https://vimeo.com/channels/staffpicks/157239808
    - watch https://www.youtube.com/watch?v=UfJ-i4Y6DGU
    - watch https://streamable.com/4914
    - watch http://www.sbs.com.au/cyclingcentral/article/2016/03/06/cancellara-etches-his-name-strade-bianche-history
"""

from __future__ import print_function

import atv
import docopt
import os
import requests
import sys
import youtube_dl

from progress.helpers import SHOW_CURSOR


ERROR, WARNING, INFO, DEBUG = [3, 2, 1, 0]

LOG_LEVELS = {
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG'
}

LOG_LEVEL = ERROR


def log(level, message):
    if level >= LOG_LEVEL:
        print('[{}] {}'.format(LOG_LEVELS[level], message))


STREAMABLE_TYPES = [
    'video/mp4',
    'application/vnd.apple.mpegurl',
    'application/x-mpegurl',
    'application/octet-stream'
]

COMPATIBLE_AUDIO_CODECS = ['mp4', 'aac']


def _video_is_compatible(v):
    log(DEBUG, 'Checking compatibility')
    log(DEBUG, v)

    ext = v['ext']
    if ext != 'mp4':
        log(DEBUG, 'Incompatible: {} is not mp4'.format(ext))
        return False

    if 'acodec' in v.keys() and not any([v['acodec'].strip().lower().startswith(x) for x in COMPATIBLE_AUDIO_CODECS]):
        log(DEBUG, 'Incompatible: {} is not a supported audio format'.format(v['acodec']))
        return False

    return True


def get_key_for_best_stream(videos):
    keys = ['tbr', 'width', 'height']

    # pick a key to use for these videos
    for picker in [all, any]:
        for k in keys:
            k_values = [v.get(k, None) for v in videos]
            log(INFO, '{}: {}'.format(k, k_values))
            if picker([v.get(k, None) for v in videos]):
                return k

    # if we haven't matched use the safest option: 'width'
    return 'width'


def get_best_stream(videos):
    best = videos[0]
    key = get_key_for_best_stream(videos)
    log(INFO, 'Using key: {}'.format(key))

    for v in videos:
        if v.get(key) > best.get(key):
            best = v

    log(DEBUG, 'Best: {}'.format(best))
    return best


def yt_dl(youtube_url, apple_tv, start=None):
    # first, a simple, custom extractor for streamable
    if 'streamable.com/' in youtube_url:
        stream_id = youtube_url.split('streamable.com/')[1].split('?')[0]
        url = 'https://cdn.streamable.com/video/mp4/{}.mp4'.format(stream_id)
        return play(url, apple_tv, start)

    # falling back to youtube_dl
    yt = youtube_dl.YoutubeDL(params={'quiet': LOG_LEVEL > INFO})
    info = yt.extract_info(youtube_url, download=False)

    # youtube playlist / embed not really supported, pick the first video
    if 'entries' in info.keys():
        info = info['entries'][0]

    compatible_videos = [x for x in info['formats'] if _video_is_compatible(x)]
    pick = get_best_stream(compatible_videos)
    play(pick['url'], apple_tv, start)


def play(stream_url, apple_tv=None, start=None):
    log(INFO, 'Stream URL: {}'.format(stream_url))
    response = requests.head(stream_url, allow_redirects=True)
    log(INFO, 'Content-Type: {}'.format(response.headers['content-type']))

    # check to see if the content type is playable
    if response.headers['content-type'] in STREAMABLE_TYPES:
        log(INFO, 'Streaming: {}'.format(stream_url))
        atv.play(stream_url, apple_tv, start)
    else:
        yt_dl(stream_url, apple_tv, start)


def main():
    args = docopt.docopt(__doc__)
    start = args['--start']

    if args['--verbose']:
        global LOG_LEVEL
        LOG_LEVEL = DEBUG

    # use the --apple-tv CLI argument (as an override), then fallback to the environment variable
    if args['--apple-tv']:
        atv_ip = args['--apple-tv']
    else:
        atv_ip = os.environ.get('APPLE_TV_IP')
        if not atv_ip:
            print("Please provide your Apple TV's IP address with the `--apple-tv` option of by setting it "
                  "in your environment with `export APPLE_TV_IP=<ip_address>`.")
            return

    try:
        play(args['<video_url>'], atv_ip, start)
    except youtube_dl.utils.DownloadError:
        log(ERROR, 'Unsupported video URL: {}\n'.format(args['<video_url>']))
        log(ERROR, 'If this url contains a streamable video that you expect to work, please file an issue on Github:\n'
                   'https://github.com/sesh/watch\n\n'
                   'Please include the full output from this command:\n'
                   'watch --verbose {}'.format(args['<video_url>']))
    except (KeyboardInterrupt, SystemExit):
        # always let the process exit cleanly
        pass

    print(SHOW_CURSOR)
    sys.exit()


if __name__ == '__main__':
    main()
