"""
Utilities to get information from Youtube-DL
"""
import io
import re
import youtube_dl
from logger import InMemoryLogger


class YoutubeDLError(Exception):
    """ For failures in the Youtbe-dl API """
    pass


def format_for_videos(urls):
    """ Get a list of formats for every video URL """
    log = InMemoryLogger()
    ydl_opts = {
        'listformats': True,
        'logger': log
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        results = []
        try:
            for url in urls:
                ydl.extract_info(url, download=False)
                stringio = io.StringIO(log.get())
                _ = [stringio.readline() for _ in range(0, 3)]
                audio_lines = [line[:-1] for line in stringio if 'audio' in line]
                splitted = [re.compile(r'[ ,]{2,}').split(line) for line in audio_lines]
                return_val = [{
                    'id': int(l[0]),
                    'container': l[1],
                    'bps': int(l[3][0:-1]),
                    'size': l[-1:][0],
                    'extra': l[4]
                } for l in splitted]
                results.append(return_val)
                log.clear()
        except youtube_dl.utils.DownloadError as error:
            raise YoutubeDLError(repr(error)[39:-3], url)
        return results


def get_urls(urls, quality_id):
    """ Get a list direct audio URL for every video URL, with some extra info """
    log = InMemoryLogger()
    ydl_opts = {
        'format': quality_id,
        'logger': log,
        'forceurl': True,
        'forcetitle': True,
        'forcethumbnail': True,
        'simulate': True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        results = []
        try:
            for url in urls:
                ydl.download([url])
                info = log.get().split('\n')[:-1][-3:]
                return_value = {
                    'title': info[0],
                    'url': info[1],
                    'thumbnail': info[2]
                }
                results.append(return_value)
        except youtube_dl.utils.DownloadError as error:
            return YoutubeDLError(repr(error)[39:-3], url)
        return results
