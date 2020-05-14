"""
Utilities to get information from Youtube-DL
"""
import io
import logging
import re
import youtube_dl
from flask import json
from .logger import InMemoryLogger


logger = logging.getLogger(__name__)


class YoutubeDLError(Exception):
    """ For failures in the Youtbe-dl API """
    pass


def _parse_video_quality(fmt: dict) -> dict:
    return {
        'id': int(fmt['format_id']),
        'container': fmt['ext'],
        'width': fmt['width'],
        'height': fmt['height'],
        'resolutionName': fmt['format_note'],
        'bps': int(fmt['tbr']),
        'codec': fmt['vcodec'],
        'fps': fmt['fps'],
        'size': fmt['filesize'],
        'hdr': 'hdr' in fmt['format_note'].lower(),
    }


def _parse_audio_quality(fmt: dict) -> dict:
    return {
        'id': int(fmt['format_id']),
        'container': fmt['ext'],
        'bps': int(fmt['tbr']),
        'sampleRate': int(fmt['asr']),
        'size': fmt['filesize'],
        'codec': fmt['acodec'],
    }


def _get_video_info(url, **kwargs):
    """ Get a list direct audio URL for every video URL, with some extra info """
    log = InMemoryLogger()
    ydl_opts = {
        'logger': log,
        'forcejson': True,
        'simulate': True,
        **kwargs,
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        lines = log.get().split('\n')
        info = json.loads(lines[-2])
        return info


def format_for_videos(urls, **kwargs):
    """ Get a list of formats for every video URL """
    joined_kwargs = ', '.join([ f'{k}: {kwargs[k]}' for k in kwargs.keys() ])
    logger.debug(f'format_for_videos: {", ".join(urls)} - {joined_kwargs}')
    results = []
    try:
        for url in urls:
            info = _get_video_info(url, **kwargs)
            formats = info['formats']

            audio_formats = [fmt for fmt in formats if fmt['acodec'] != 'none' and fmt['vcodec'] == 'none']
            video_formats = [fmt for fmt in formats if fmt['acodec'] == 'none' and fmt['vcodec'] != 'none']

            audio_qualities = [_parse_audio_quality(l) for l in audio_formats]
            video_qualities = [_parse_video_quality(l) for l in video_formats]

            model = {
                'audio': audio_qualities,
                'video': video_qualities,
            }
            results.append(model)
            logger.debug('[format_for_videos] Output for %s:\n%s', url, repr(model))
    except youtube_dl.utils.DownloadError as error:
        logger.warning('[format_for_videos] Error for %s: %s', url, repr(error))
        raise YoutubeDLError(repr(error), url)
    return results


def get_urls(urls, quality_id: str='bestvideo/best,bestaudio/best', **kwargs):
    """ Get a list direct audio URL for every video URL, with some extra info """
    joined_kwargs = ', '.join([ f'{k}: {kwargs[k]}' for k in kwargs.keys() ])
    logger.debug(f'get_urls: {", ".join(urls)} - {quality_id} - {joined_kwargs}')
    results = []
    try:
        for url in urls:
            info = _get_video_info(url, format=quality_id, **kwargs)
            if quality_id == 'bestvideo/best,bestaudio/best':
                formats = info['formats'][::-1]
                audio_format = next(iter((fmt for fmt in formats if fmt['acodec'] != 'none' and fmt['vcodec'] == 'none')))
                video_format = next(iter((fmt for fmt in formats if fmt['acodec'] == 'none' and fmt['vcodec'] != 'none')))
                requested_formats = [video_format, audio_format]
            else:
                requested_formats = info.get('requested_formats', [info])

            return_value = {
                'title': info['title'],
                'description': info['description'],
                'duration': info['duration'],
                'thumbnail': info['thumbnail'],
                'likes': info['like_count'],
                'dislikes': info['dislike_count'],
                'views': info['view_count'],
                'urls': {fmt['format_id']: fmt['url'] for fmt in requested_formats},
            }
            results.append(return_value)
            logger.debug('[get_urls] Output for %s@%s:\n%s', url, quality_id, repr(return_value))
    except youtube_dl.utils.DownloadError as error:
        logger.warning('[format_for_videos] Error for %s@%s: %s', url, quality_id, repr(error)[:-3])
        raise YoutubeDLError(repr(error)[:-3], url)
    return results
