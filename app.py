import logging, io, re, json
from flask import Flask, request, render_template, jsonify
from werkzeug.contrib.cache import SimpleCache
import youtube_dl


app = Flask(__name__)
cache = SimpleCache()


class InMemoryLogger(object):
    def __init__(self):
        self.__stream = io.StringIO()

    def debug(self, msg):
        self.__stream.write(msg)
        self.__stream.write('\n')

    def warning(self, msg):
        self.debug(msg)

    def error(self, msg):
        self.__stream.write('[error] ')
        self.debug(msg)

    def get(self):
        return self.__stream.getvalue()


@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/api/<yid>/formats", methods=['GET'])
def formats(yid):
    global cache
    cache_val = cache.get(f'yt_{yid}_formats')
    if cache_val is not None:
        return jsonify(json.loads(cache_val))

    log = InMemoryLogger()
    ydl_opts = {
        'listformats': True,
        'logger': log
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(f'https://www.youtube.com/watch?v={yid}', download=False)
        stringio = io.StringIO(log.get())
        [ stringio.readline() for _ in range(0, 3) ]
        audio_lines = [ line[:-1] for line in stringio if 'audio' in line ]
        splitted = [ re.compile(r'[ ,]{2,}').split(line) for line in audio_lines ]
        return_val = [ {
            'id': l[0],
            'container': l[1],
            'bps': l[3],
            'size': l[-1:][0],
            'extra': l[4]
        } for l in splitted ]
        cache.set(f'yt_{yid}_formats', json.dumps(return_val))
        return jsonify(return_val)

@app.route("/api/<yid>", methods=['GET'])
def get_url(yid):
    global cache
    quality_id = request.args.get('quality_id', 'bestaudio/best')
    cache_val = cache.get(f'yt_{yid}_{quality_id}')
    if cache_val is not None:
        cache_val = json.loads(cache_val)
        if cache_val['status'] == 'ok':
            return jsonify(cache_val['data'])
        else:
            return jsonify(cache_val['data']), 404

    log = InMemoryLogger()
    ydl_opts = {
        'format': quality_id,
        'logger': log,
        'forceurl': True,
        'simulate': True
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([f'https://www.youtube.com/watch?v={yid}'])
            url = log.get().split('\n')[:-1][-1:][0]
            cache.set(f'yt_{yid}_{quality_id}', f'{{"status":"ok", "data":{{"url": "{url}"}}}}', timeout=10*60)
            return jsonify({'url': url})
        except youtube_dl.utils.DownloadError as e:
            cache.set(f'yt_{yid}_{quality_id}', f'{{"status":"error", "data":{{"error": "{repr(e)[39:-3]}"}}}}')
            return jsonify({'error': repr(e)[39:-3]}), 404

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
            return jsonify({'error': repr(e)[39:-3]}), 404


if __name__ == '__main__':
    if os.environ['PORT']:
        app.run(host='127.0.0.1', port=int(os.environ['PORT'])
    else:
        app.run(host='127.0.0.1', port=5000)
