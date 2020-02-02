from collections import OrderedDict
import logging
import os

from flask import Flask, request, Response, make_response
from flask_cache import Cache
from flask_cors import cross_origin

import ytdl_audio_api.ytdl as ytdl
from .decorator import cache_aware, log_request
from .http_pipe import pipe, pipe_headers

app = Flask(__name__)
logging.basicConfig(level=logging.getLevelName(os.environ.get('LOGGING_LEVEL', 'WARN')))
logger = logging.getLogger(__name__)

if 'REDIS_URL' in os.environ:
    logger.info('Using redis cache "%s"', os.environ['REDIS'])
    cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': os.environ['REDIS_URL']},
                  with_jinja2_ext=False)
elif 'REDIS' in os.environ:
    logger.info('Using redis cache "%s"', os.environ['REDIS'])
    cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': os.environ['REDIS']}, with_jinja2_ext=False)
else:
    logger.info('Using in-memory cache')
    cache = Cache(app, config={'CACHE_TYPE': 'simple'}, with_jinja2_ext=False)

PROXY = os.environ.get('PROXY')
FALLBACK_PROXY = os.environ.get('FALLBACK_PROXY')


@app.route("/")
@log_request(logger)
def hello():
    res = make_response('''
<html lang="en">
<head>
    <title>YoutubeDL Audio API</title>
</head>
<body>
    <p>
        Want to know how it works? See
        <a href="https://github.com/melchor629/youtubedl-audio-api" target="_blank" rel="nofollow">the repo</a>
    </p>
    <p>
        Want an example?
        <a href="https://youtubeaudio.majorcadevs.com" target="_blank" rel="nofollow">See that page</a>
    </p>
</body>
</html
    ''')  # type: Response
    res.headers.add_header('Cache-Control', 'private, max-age=86400')
    return res


@app.route("/api/health")
@log_request(logger)
@cross_origin()
def health(**kwargs):
    return 'OK'


@app.route("/api/<yid>/formats/", methods=['GET'])
@app.route("/api/<yid>/formats", methods=['GET'])
@log_request(logger)
@cross_origin()
@cache_aware(cache, 'yt_{yid}_formats')
def formats(yid, **kwargs):
    try:
        return ytdl.format_for_videos([f'https://www.youtube.com/watch?v={yid}'], proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.format_for_videos([f'https://www.youtube.com/watch?v={yid}'], proxy=FALLBACK_PROXY)[0]


@app.route("/api/<yid>/", methods=['GET'])
@app.route("/api/<yid>", methods=['GET'])
@log_request(logger)
@cross_origin()
@cache_aware(cache, 'yt_{yid}_bestaudio', timeout=10 * 60)
def get_url_default_quality(yid, **kwargs):
    logger.info(f'/api/{yid}')
    try:
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], proxy=FALLBACK_PROXY)[0]


@app.route("/api/<yid>/<quality_id>/", methods=['GET'])
@app.route("/api/<yid>/<quality_id>", methods=['GET'])
@log_request(logger)
@cross_origin()
@cache_aware(cache, 'yt_{yid}_{quality_id}', timeout=10 * 60)
def get_url(yid, quality_id, **kwargs):
    try:
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], quality_id, proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], quality_id, proxy=FALLBACK_PROXY)[0]


@app.route("/api/<yid>/<quality_id>/passthrough/", methods=["HEAD"])
@app.route("/api/<yid>/<quality_id>/passthrough", methods=["HEAD"])
@log_request(logger)
@cross_origin()
def passthrough_head(yid, quality_id, **kwargs):
    resp = get_url(yid=yid, quality_id=quality_id)
    if resp.status_code == 200:
        for proxy_url in list(OrderedDict.fromkeys([ None, PROXY, FALLBACK_PROXY ])):
            headers = pipe_headers(request.headers, resp.obj['url'], proxy_url)
            if headers is not None:
                return Response(headers=headers)
        return 'Cannot obtain audio', 404
    else:
        return Response(headers=resp.headers)


@app.route("/api/<yid>/<quality_id>/passthrough/", methods=["GET"])
@app.route("/api/<yid>/<quality_id>/passthrough", methods=["GET"])
@log_request(logger)
@cross_origin()
def passthrough(yid, quality_id, **kwargs):
    resp = get_url(yid=yid, quality_id=quality_id)
    if resp.status_code == 200:
        for proxy_url in list(OrderedDict.fromkeys([ None, PROXY, FALLBACK_PROXY ])):
            logger.warning(f'f {proxy_url}')
            stream, headers = pipe(request, resp.obj['url'], proxy_url)
            if stream is not None:
                return Response(stream, headers=headers)
        return 'Cannot obtain audio', 404
    else:
        return resp


if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        port = int(os.environ['PORT'])
        logger.info(f'Listening at http://0.0.0.0:{port}')
        app.run(host='0.0.0.0', port=port)
    else:
        logger.info(f'Listening at http://127.0.0.1:5000')
        app.run(host='127.0.0.1', port=5000)
