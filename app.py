import os

from flask import Flask, request, render_template
from flask_cors import cross_origin

import ytdl
from decorator import cache_aware


app = Flask(__name__)


@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/api/<yid>/formats", methods=['GET'])
@cross_origin()
@cache_aware('yt_{yid}_formats')
def formats(yid):
    return ytdl.format_for_videos([f'https://www.youtube.com/watch?v={yid}'])[0]

@app.route("/api/<yid>", methods=['GET'])
@cross_origin()
@cache_aware('yt_{yid}_bestaudio')
def get_url_default_quality(yid):
    return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], 'bestaudio/best')[0]

@app.route("/api/<yid>/<quality_id>", methods=['GET'])
@cross_origin()
@cache_aware('yt_{yid}_{quality_id}', timeout=10*60)
def get_url(yid, quality_id):
    return ytdl.get_urls([f'https://www.youtube.com/watch?v={yid}'], quality_id)[0]

@app.route("/api/<yid>/player", methods=['GET'])
def play_url(yid):
    log = InMemoryLogger()
    ydl_opts = {
        'format': request.args.get('quality_id', 'bestaudio/best'),
        'logger': log,
        'forceurl': True,
        'simulate': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f'https://www.youtube.com/watch?v={yid}'])
            url = log.get().split('\n')[:-1][-1:][0]
            return """
            <html>
            <head>
                <title>Playing {0}</title>
                <meta charset="utf-8">
            </head>
            <body>
                <audio src="{1}" autoplay controls></audio><br/>
                <pre><code>Youtube ID: {0}
Format ID: {2}
Audio URL: {1}</code></pre>
            </body>
            </html>
            """.format(yid, url, request.args.get('quality_id', 'bestaudio/best'))
        except youtube_dl.utils.DownloadError as e:
            return repr(e)[39:-3], 404


if __name__ == '__main__':
    if os.environ.get('PORT') is not None:
        app.run(host='0.0.0.0', port=int(os.environ['PORT']))
    else:
        app.run(host='127.0.0.1', port=5000)
