# YouTube-DL Audio API

An pythonic RESTful API for getting URL of YouTube videos with only audio, perfect for playing in background reducing the network bandwith. Uses [youtube-dl][1] for the queries, and [Flask][2] for the web microframework.

## Requirements

The project requires Python 3.3 or higher, and install some dependencies.

```bash
pip install -r requirements.txt
```

For local development, a `pyenv` or `virtualenv` is highly recomended. There's a [Dockerfile][3] available for creating an image.

For **macOS**, use `brew` to install python 3:

```bash
brew install python3
pip3 install -r requirements.txt
```

You can use the Docker image to use it in development. (see Docker section) This command should do the trick:

```bash
docker container run --rm -it -p 5000:5000 -v "$PWD":/opt/yt-audio-api ytdl-audio-api
```

## Using the web

By default, running the app with `python app.py` will run on http://localhost:5000 . If you set the environment variable `PORT` to some port, it will listen for everyone at the specified port.

The app can be scalated using `gunicorn -c gunicorn.conf ytdl_audio_api.wsgi`. Is configured to use `gevent` for asynchronous serving.

You can deploy the app to [Heroku][4] or into a [Docker][3] environment.

## Example

We did [a demo page][5] for that.

Also, I have a [Heroku instance][6] running with a little example.

## RESTful API

### GET /api/\<youtube-id\>

Gets the audio URL, the title and the thumbnail of the video in the best audio quality (usually Opus 160Kbps VBR in webm container). The url differ change between calls.

An example of https://yt-audio-api.herokuapp.com/api/0RLvtm0EghQ:

```json
{
  "thumbnail": "https://i.ytimg.com/vi/0RLvtm0EghQ/hqdefault.jpg",
  "title": "Floating Points - Kuiper (Live on KEXP)",
  "url": "https://..."
}
```

### GET /api/\<youtube-id\>/\<quality-id\>

The same as before, but changing the audio quality to the id (see next section).

### GET /api/\<youtube-id\>/formats

Returns a list of different audio formats available in the servers to play directly. The `id` field can be used in the upper section in `<quality-id>` path field.

An example of https://yt-audio-api.herokuapp.com/api/0RLvtm0EghQ/formats:

```json
[
  {
    "bps": 63,
    "container": "webm",
    "extra": "opus @ 50k",
    "id": 249,
    "size": "6.04MiB"
  },
  {
    "bps": 88,
    "container": "webm",
    "extra": "opus @ 70k",
    "id": 250,
    "size": "7.90MiB"
  },
  {
    "bps": 129,
    "container": "m4a",
    "extra": "m4a_dash container",
    "id": 140,
    "size": "15.04MiB"
  },
  {
    "bps": 136,
    "container": "webm",
    "extra": "vorbis@128k",
    "id": 171,
    "size": "13.23MiB"
  },
  {
    "bps": 166,
    "container": "webm",
    "extra": "opus @160k",
    "id": 251,
    "size": "15.33MiB"
  }
]
```

## Docker

By default, the Docker image created will publish the web in the port 5000. Uses the `python:3` image.

An example of building the image, running and testing:

```bash
docker image build -t yt-audio-api .
docker container run -d --rm -p 5000:5000 yt-audio-api
curl http://localhost:5000/api/0RLvtm0EghQ
```

## Cache
Some request can be cached using Redis. The only thing you must do to use Redis is setting the environment
variable `REDIS` (o `REDIS_URL` useful for Heroku) with the url of the server.

  [1]: https://rg3.github.io/youtube-dl/
  [2]: http://flask.pocoo.org
  [3]: https://docker.com
  [4]: https://heroku.com
  [5]: https://github.com/MajorcaDevs/youtubeAudio
  [6]: https://yt-audio-api.herokuapp.com/
