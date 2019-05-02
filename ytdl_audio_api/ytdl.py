"""
Utilities to get information from Youtube-DL
"""
import io
import logging
import re
import youtube_dl
from .logger import InMemoryLogger


logger = logging.getLogger(__name__)


class YoutubeDLError(Exception):
    """ For failures in the Youtbe-dl API """
    pass


def format_for_videos(urls, **kwargs):
    """ Get a list of formats for every video URL """
    log = InMemoryLogger()
    ydl_opts = {
        'listformats': True,
        'logger': log,
        **kwargs,
    }

    joined_kwargs = ', '.join([ f'{k}: {kwargs[k]}' for k in kwargs.keys() ])
    logger.debug(f'format_for_videos: {", ".join(urls)} - {joined_kwargs}')
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
                    'extra': l[-2]
                } for l in splitted]
                results.append(return_val)
                log.clear()
                logger.debug('[format_for_videos] Output for %s:\n%s', url, repr(return_val))
        except youtube_dl.utils.DownloadError as error:
            logger.warning('[format_for_videos] Error for %s: %s', url, repr(error))
            raise YoutubeDLError(repr(error), url)
        return results


def get_urls(urls, quality_id='bestaudio/best', **kwargs):
    """ Get a list direct audio URL for every video URL, with some extra info """
    log = InMemoryLogger()
    ydl_opts = {
        'format': quality_id,
        'logger': log,
        'forceurl': True,
        'forcetitle': True,
        'forcethumbnail': True,
        'simulate': True,
        **kwargs,
    }

    joined_kwargs = ', '.join([ f'{k}: {kwargs[k]}' for k in kwargs.keys() ])
    logger.debug(f'get_urls: {", ".join(urls)} - {quality_id} - {joined_kwargs}')
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
                logger.debug('[get_urls] Output for %s@%s:\n%s', url, quality_id, repr(return_value))
        except youtube_dl.utils.DownloadError as error:
            logger.warning('[format_for_videos] Error for %s@%s: %s', url, quality_id, repr(error)[:-3])
            raise YoutubeDLError(repr(error)[:-3], url)
        return results
