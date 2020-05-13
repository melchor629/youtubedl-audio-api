# YouTube-DL Audio API

An pythonic RESTful API for getting URL of YouTube videos with only audio or video+audio, perfect for playing in background reducing the network bandwith. Uses [youtube-dl][1] for the queries, and [Flask][2] for the web microframework.

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
docker container run --rm -it -p 5000:5000 melchor9000/youtubedl-audio-api
```

## Using the web

By default, running the app with `python app.py` will run on http://localhost:5000 . If you set the environment variable `PORT` to some port, it will listen for everyone at the specified port.

The app can be scalated using `gunicorn -c gunicorn.py ytdl_audio_api.wsgi`. Is configured to use `gevent` for asynchronous serving.

You can deploy the app to [Heroku][4] or into a [Docker][3] environment.

> **Note**: by default it will use `2 * Cores + 1` workers. You can change this using the `WORKERS`
> environment variable. In Heroku this is mandatory, so add a "Config Var" called `WORKERS` and put
> a value of 1 or 2 (if using the free dyno).

## Example

We did [a demo page][5] for that.

Also, I have an [instance][6] running with a little example.

## RESTful API

### GET /api/\<youtube-id\>

Gets the video and audio URLs, the title and the thumbnail of the video in the best video/audio quality. The urls differ change between calls. The first URL corresponds to the video, and the second one to the audio.

An example of <https://youtubeaudio.majorcadevs.com/api/0RLvtm0EghQ>:

```json
{
  "description": "http://KEXP.ORG presents Floating Points performing \"Kuiper\" live in the KEXP studio. Recorded May 3, 2016.\n\nHost: Larry Rose\nAudio Engineer: Michael Parker & Kevin Suggs\nCameras: Jim Beckmann, Alaia D'Alessandro & Scott Holpainen\nEditor: Scott Holpainen\n\nPhoto thumbnail by Matthew B. Thompson\n\nhttp://kexp.org\nhttp://www.floatingpoints.co.uk",
  "dislikes": 8,
  "duration": 993,
  "likes": 864,
  "thumbnail": "https://i.ytimg.com/vi/0RLvtm0EghQ/hqdefault.jpg",
  "title": "Floating Points - Kuiper (Live on KEXP)",
  "urls": {
    "137": "https://...",
    "140": "https://..."
  },
  "views": 44087
}
```

### GET /api/\<youtube-id\>/\<quality-id\>

The same as before, but selecting only a video or audio quality through the id selected. The response will only contain one URL (for the selected quality).

An example of <https://youtubeaudio.majorcadevs.com/api/0RLvtm0EghQ/140>

```json
{
  "description": "http://KEXP.ORG presents Floating Points performing \"Kuiper\" live in the KEXP studio. Recorded May 3, 2016.\n\nHost: Larry Rose\nAudio Engineer: Michael Parker & Kevin Suggs\nCameras: Jim Beckmann, Alaia D'Alessandro & Scott Holpainen\nEditor: Scott Holpainen\n\nPhoto thumbnail by Matthew B. Thompson\n\nhttp://kexp.org\nhttp://www.floatingpoints.co.uk",
  "dislikes": 8,
  "duration": 993,
  "likes": 864,
  "thumbnail": "https://i.ytimg.com/vi/0RLvtm0EghQ/hqdefault.jpg",
  "title": "Floating Points - Kuiper (Live on KEXP)",
  "urls": {
    "140": "https://..."
  },
  "views": 44087
}
```

### GET /api/\<youtube-id\>/\<quality-id1\>,\<quality-id2\>

The same as before, but changing the video and audio quality to the selected ids. The response will contain two URLs: first corresponding to the `<quality-id1>` and the second one corresponding to `<quality-id2>`. The idea is to put a video and audio qualities, but nothing prevents you to put two videos or two audio qualities.

An example of <https://youtubeaudio.majorcadevs.com/api/0RLvtm0EghQ/140,137>

```json
{
  "description": "http://KEXP.ORG presents Floating Points performing \"Kuiper\" live in the KEXP studio. Recorded May 3, 2016.\n\nHost: Larry Rose\nAudio Engineer: Michael Parker & Kevin Suggs\nCameras: Jim Beckmann, Alaia D'Alessandro & Scott Holpainen\nEditor: Scott Holpainen\n\nPhoto thumbnail by Matthew B. Thompson\n\nhttp://kexp.org\nhttp://www.floatingpoints.co.uk",
  "dislikes": 8,
  "duration": 993,
  "likes": 864,
  "thumbnail": "https://i.ytimg.com/vi/0RLvtm0EghQ/hqdefault.jpg",
  "title": "Floating Points - Kuiper (Live on KEXP)",
  "urls": {
    "137": "https://...",
    "140": "https://..."
  },
  "views": 44087
}
```

### GET /api/\<youtube-id\>/formats

Returns a list of different audio formats available in the servers to play directly. The `id` field can be used in the upper section in `<quality-id>` path field.

An example of <https://youtubeaudio.majorcadevs.com/api/0RLvtm0EghQ/formats>:

```json
{
  "audio": [
    {
      "bps": 69,
      "container": "webm",
      "extra": "opus @ 50k (48000Hz)",
      "id": 249,
      "size": "6.05MiB"
    },
    {
      "bps": 84,
      "container": "webm",
      "extra": "opus @ 70k (48000Hz)",
      "id": 250,
      "size": "7.89MiB"
    },
    {
      "bps": 129,
      "container": "m4a",
      "extra": "mp4a.40.2@128k (44100Hz)",
      "id": 140,
      "size": "15.04MiB"
    },
    {
      "bps": 157,
      "container": "webm",
      "extra": "opus @160k (48000Hz)",
      "id": 251,
      "size": "15.34MiB"
    }
  ],
  "video": [
    {
      "bps": 99,
      "codec": "vp9",
      "container": "webm",
      "extra": "only",
      "fps": 24,
      "id": 278,
      "resolution": "256x144",
      "resolutionName": "144p",
      "size": "10.64MiB"
    },
    {
      "bps": 111,
      "codec": "avc1.4d400c",
      "container": "mp4",
      "extra": "only",
      "fps": 24,
      "id": 160,
      "resolution": "256x144",
      "resolutionName": "144p",
      "size": "7.48MiB"
    },
    {
      "bps": 230,
      "codec": "vp9",
      "container": "webm",
      "extra": "only",
      "fps": 24,
      "id": 242,
      "resolution": "426x240",
      "resolutionName": "240p",
      "size": "19.75MiB"
    },
    {
      "bps": 244,
      "codec": "avc1.4d4015",
      "container": "mp4",
      "extra": "only",
      "fps": 24,
      "id": 133,
      "resolution": "426x240",
      "resolutionName": "240p",
      "size": "13.87MiB"
    },
    {
      "bps": 430,
      "codec": "vp9",
      "container": "webm",
      "extra": "only",
      "fps": 24,
      "id": 243,
      "resolution": "640x360",
      "resolutionName": "360p",
      "size": "35.49MiB"
    },
    {
      "bps": 633,
      "codec": "avc1.4d401e",
      "container": "mp4",
      "extra": "only",
      "fps": 24,
      "id": 134,
      "resolution": "640x360",
      "resolutionName": "360p",
      "size": "33.68MiB"
    },
    {
      "bps": 760,
      "codec": "vp9",
      "container": "webm",
      "extra": "only",
      "fps": 24,
      "id": 244,
      "resolution": "854x480",
      "resolutionName": "480p",
      "size": "59.08MiB"
    },
    {
      "bps": 1159,
      "codec": "avc1.4d401e",
      "container": "mp4",
      "extra": "only",
      "fps": 24,
      "id": 135,
      "resolution": "854x480",
      "resolutionName": "480p",
      "size": "64.65MiB"
    },
    {
      "bps": 1512,
      "codec": "vp9",
      "container": "webm",
      "extra": "only",
      "fps": 24,
      "id": 247,
      "resolution": "1280x720",
      "resolutionName": "720p",
      "size": "114.01MiB"
    },
    {
      "bps": 2305,
      "codec": "avc1.4d401f",
      "container": "mp4",
      "extra": "only",
      "fps": 24,
      "id": 136,
      "resolution": "1280x720",
      "resolutionName": "720p",
      "size": "119.61MiB"
    },
    {
      "bps": 2644,
      "codec": "vp9",
      "container": "webm",
      "extra": "only",
      "fps": 24,
      "id": 248,
      "resolution": "1920x1080",
      "resolutionName": "1080p",
      "size": "198.28MiB"
    },
    {
      "bps": 3878,
      "codec": "avc1.640028",
      "container": "mp4",
      "extra": "only",
      "fps": 24,
      "id": 137,
      "resolution": "1920x1080",
      "resolutionName": "1080p",
      "size": "218.99MiB"
    }
  ]
}
```

## Docker

By default, the Docker image created will publish the web in the port 5000. Uses the `python:3` image.

An example of building the image, running and testing:

```bash
docker image build -t yt-audio-api .
docker container run -d --rm -p 5000:5000 yt-audio-api # or melchor9000/youtubedl-audio-api from Docker Hub
curl http://localhost:5000/api/0RLvtm0EghQ
```

It is available a `docker-compose.yaml` file to test it out. Uses the image from Docker Hub and a redis server for caching.

## Cache
Some request can be cached using Redis. The only thing you must do to use Redis is setting the environment
variable `REDIS` (or `REDIS_URL` useful for Heroku) with the url of the server.

## Logging
The server has logging for some points of functions. To modify the logging level, set `LOGGING_LEVEL` environment variable to the value you want. Valid values are `CRITICAL`, `FATAL`, `ERROR`, `WARNING`, `WARN`, `INFO`, `DEBUG` or `NOTSET`, see [logging][7] from Python.

## Proxy

You can set a proxy with the environment variable `PROXY`. Supported proxy protocols are http, https and socks5.

If you want to use a proxy as a fallback, use `FALLBACK_PROXY`. This will be used if any call to the YT API fails.

## Pretty JSONs

If, for some reason, you want to get the JSONs in a pretty format, set `JSONIFY_PRETTYPRINT_REGULAR` environment variable to `true`.

  [1]: https://rg3.github.io/youtube-dl/
  [2]: http://flask.pocoo.org
  [3]: https://docker.com
  [4]: https://heroku.com
  [5]: https://github.com/MajorcaDevs/youtubeAudio
  [6]: https://youtubeaudio.majorcadevs.com/api/
  [7]: https://docs.python.org/3/library/logging.html#logging-levels
