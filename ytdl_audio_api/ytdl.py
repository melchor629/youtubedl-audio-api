"""
Utilities to get information from Youtube-DL
"""
import logging
import subprocess
from typing import List
from flask import json


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
        'bps': float(fmt['tbr']),
        'codec': fmt['vcodec'],
        'fps': fmt['fps'],
        'size': fmt['filesize'],
        'hdr': 'hdr' in fmt['dynamic_range'].lower(),
    }


def _parse_audio_quality(fmt: dict) -> dict:
    return {
        'id': int(fmt['format_id']),
        'container': fmt['ext'],
        'bps': float(fmt['tbr']),
        'sampleRate': int(fmt['asr']),
        'size': fmt['filesize'],
        'codec': fmt['acodec'],
        'channels': fmt['audio_channels'],
    }


def _get_video_info(url: str, **kwargs) -> dict:
    """ Get a list direct audio URL for every video URL, with some extra info """
    ydl_opts = [
        '--dump-json',
        '--no-progress',
        '--simulate',
        *[arg for pair in [
            [f'--{key}', value] for key, value in kwargs.items() if value is not None
        ] for arg in pair],
        url,
    ]

    logger.debug(f'_get_video_info: invoking yt-dlp with args {ydl_opts}')
    result = subprocess.run(
        ['yt-dlp', *ydl_opts],
        capture_output=True,
        encoding='utf-8',
    )

    if result.returncode != 0:
        logger.warning(f'_get_video_info: failed with status {result.returncode}\n{result.stderr}')
        raise YoutubeDLError(result.stderr, url)

    info = [json.loads(doc) for doc in result.stdout.split('\n') if doc and doc[0] == '{']
    if len(info) == 0:
        raise YoutubeDLError('yt-dlp did not return anything', url)

    return info[0]


def get_video_info(url: str, **kwargs) -> dict:
    """ Gets what yt-dlp returns for the video """
    return _get_video_info(url, **kwargs)


def format_for_videos(urls: List[str], **kwargs):
    """ Get a list of formats for every video URL """
    joined_kwargs = ', '.join([ f'{k}: {kwargs[k]}' for k in kwargs.keys() ])
    logger.debug(f'format_for_videos: {", ".join(urls)} - {joined_kwargs}')
    results = []

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

    return results


def get_urls(urls: List[str], quality_id: str='bestvideo/best+bestaudio/best', **kwargs):
    """ Get a list direct audio URL for every video URL, with some extra info """
    joined_kwargs = ', '.join([ f'{k}: {kwargs[k]}' for k in kwargs.keys() ])
    logger.debug(f'get_urls: {", ".join(urls)} - {quality_id} - {joined_kwargs}')
    results = []

    for url in urls:
        info = _get_video_info(url, format=quality_id, **kwargs)
        if quality_id == 'bestvideo/best+bestaudio/best':
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
            'dislikes': info.get('dislike_count', None),
            'views': info['view_count'],
            'urls': {fmt['format_id']: fmt['url'] for fmt in requested_formats},
        }
        results.append(return_value)
        logger.debug('[get_urls] Output for %s@%s:\n%s', url, quality_id, repr(return_value))
    return results
