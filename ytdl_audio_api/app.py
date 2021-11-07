from collections import OrderedDict
import logging
import os

from flask import Flask, request, Response, make_response
from flask_caching import Cache
from flask_cors import cross_origin
from werkzeug.middleware.proxy_fix import ProxyFix

import ytdl_audio_api.ytdl as ytdl
from .decorator import cache_aware, log_request
from .http_pipe import pipe, pipe_headers

app = Flask(__name__)
logging.basicConfig(level=logging.getLevelName(os.environ.get('LOGGING_LEVEL', 'WARN')))
logger = logging.getLogger(__name__)

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = os.environ.get('JSONIFY_PRETTYPRINT_REGULAR', '').lower() == 'true'

if 'REDIS_URL' in os.environ:
    logger.info('Using redis cache "%s"', os.environ['REDIS_URL'])
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
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '').split(',')

if len(CORS_ORIGINS) == 0:
    CORS_ORIGINS = '*'
elif len(CORS_ORIGINS) == 1 and CORS_ORIGINS[0] == '*':
    CORS_ORIGINS = '*'

if not app.config['DEBUG']:
    logger.info('Applying proxy fix')
    # https://werkzeug.palletsprojects.com/en/2.0.x/middleware/proxy_fix/#werkzeug.middleware.proxy_fix.ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)


@app.get("/")
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
        <a href="https://github.com/melchor629/youtubedl-audio-api" target="_blank" rel="nofollow">the repo</a>.
        Also it is available the OpenAPI spec to check it out:
        <a href="oas.yaml" target="_blank" rel="nofollow">oas.yaml</a>.
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

@app.get('/oas.yaml')
@app.get('/oas.yml')
@app.get('/swagger.yaml')
@app.get('/swagger.yml')
@log_request(logger)
@cross_origin(origins='*')
def yaml(**kwargs):
    with open('ytdl_audio_api/oas.yaml', 'r') as oas:
        oas_yaml = [line for line in oas]
        if request.host_url:
            oas_yaml[8] = f'- url: "{request.host_url}"\n'
        oas_yaml = ''.join(oas_yaml)

    response = make_response(oas_yaml)
    response.headers['Content-Type'] = 'application/x-yaml'
    return response


@app.get('/api/health', strict_slashes=False)
@cross_origin(origins=CORS_ORIGINS)
def health(**kwargs):
    return 'OK'


@app.get('/api/<yid>/formats', strict_slashes=False)
@log_request(logger)
@cross_origin(origins=CORS_ORIGINS)
@cache_aware(cache, 'yt_{yid}_formats')
def formats(yid, **kwargs):
    try:
        return ytdl.format_for_videos([f'https://www.youtube.com/watch?v={yid}'], proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.format_for_videos([f'https://www.youtube.com/watch?v={yid}'], proxy=FALLBACK_PROXY)[0]


@app.get('/api/<yid>', strict_slashes=False)
@log_request(logger)
@cross_origin(origins=CORS_ORIGINS)
@cache_aware(cache, 'yt_{yid}_bestaudio', timeout=10 * 60)
def get_url_default_quality(yid, **kwargs):
    logger.info(f'/api/{yid}')
    try:
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], proxy=FALLBACK_PROXY)[0]


@app.get('/api/<yid>/<int:quality_id>', strict_slashes=False)
@log_request(logger)
@cross_origin(origins=CORS_ORIGINS)
@cache_aware(cache, 'yt_{yid}_{quality_id}', timeout=10 * 60)
def get_url(yid, quality_id, **kwargs):
    try:
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], str(quality_id), proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], str(quality_id), proxy=FALLBACK_PROXY)[0]


@app.get('/api/<yid>/<int:quality_id1>,<int:quality_id2>', strict_slashes=False)
@log_request(logger)
@cross_origin(origins=CORS_ORIGINS)
@cache_aware(cache, 'yt_{yid}_{quality_id1},{quality_id2}', timeout=10 * 60)
def get_url_with_video(yid, quality_id1, quality_id2, **kwargs):
    quality_id = f'{quality_id1}+{quality_id2}'
    try:
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], quality_id, proxy=PROXY)[0]
    except ytdl.YoutubeDLError as e:
        if FALLBACK_PROXY is None or FALLBACK_PROXY == '':
            raise e
        return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], quality_id, proxy=FALLBACK_PROXY)[0]


@app.route('/api/<yid>/<int:quality_id>/passthrough', methods=['HEAD'], strict_slashes=False)
@log_request(logger)
@cross_origin(origins=CORS_ORIGINS)
def passthrough_head(yid, quality_id, **kwargs):
    resp = get_url(yid=yid, quality_id=quality_id)
    if resp.status_code == 200:
        for proxy_url in list(OrderedDict.fromkeys([ None, PROXY, FALLBACK_PROXY ])):
            headers = pipe_headers(request.headers, resp.obj['url'], proxy_url)
            if headers is not None:
                return Response(headers=headers)
        return 'Cannot obtain stream', 404
    else:
        return Response(headers=resp.headers)


@app.get('/api/<yid>/<int:quality_id>/passthrough', strict_slashes=False)
@log_request(logger)
@cross_origin(origins=CORS_ORIGINS)
def passthrough(yid, quality_id, **kwargs):
    resp = get_url(yid=yid, quality_id=quality_id)
    if resp.status_code == 200:
        for proxy_url in list(OrderedDict.fromkeys([ None, PROXY, FALLBACK_PROXY ])):
            logger.warning(f'f {proxy_url}')
            stream, headers = pipe(request, resp.obj['url'], proxy_url)
            if stream is not None:
                return Response(stream, headers=headers)
        return 'Cannot obtain stream', 404
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
