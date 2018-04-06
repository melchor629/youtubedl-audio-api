import os

from flask import Flask, request, Response
from flask_cors import cross_origin

import ytdl_audio_api.ytdl as ytdl
from .decorator import cache_aware
from .http_pipe import pipe, pipe_headers

app = Flask(__name__)


@app.route("/")
def hello():
    return '''
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
        <a href="http://majorcadevs.github.io/youtubeAudio/" target="_blank" rel="nofollow">See that page</a>
    </p>
</body>
</html
    '''


@app.route("/api/<yid>/formats", methods=['GET'])
@cross_origin()
@cache_aware('yt_{yid}_formats')
def formats(yid, **kwargs):
    return ytdl.format_for_videos([f'https://www.youtube.com/watch?v={yid}'])[0]


@app.route("/api/<yid>", methods=['GET'])
@cross_origin()
@cache_aware('yt_{yid}_bestaudio', timeout=10 * 60)
def get_url_default_quality(yid, **kwargs):
    return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'])[0]


@app.route("/api/<yid>/<quality_id>", methods=['GET'])
@cross_origin()
@cache_aware('yt_{yid}_{quality_id}', timeout=10 * 60)
def get_url(yid, quality_id, **kwargs):
    return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], quality_id)[0]


@app.route("/api/<yid>/<quality_id>/passthrough", methods=["HEAD"])
@cross_origin()
def passthrough_head(yid, quality_id, **kwargs):
    resp = get_url(yid=yid, quality_id=quality_id)
    if resp.status_code == 200:
        headers = pipe_headers(request, resp.obj['url'])
        return Response(headers=headers)
    else:
        return Response(headers=resp.headers)


@app.route("/api/<yid>/<quality_id>/passthrough", methods=["GET"])
@cross_origin()
def passthrough(yid, quality_id, **kwargs):
    resp = get_url(yid=yid, quality_id=quality_id)
    if resp.status_code == 200:
        stream, headers = pipe(request, resp.obj['url'])
        return Response(stream, headers=headers)
    else:
        return resp


if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        app.run(host='0.0.0.0', port=int(os.environ['PORT']))
    else:
        app.run(host='127.0.0.1', port=5000)
