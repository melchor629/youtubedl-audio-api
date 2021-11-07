# YouTube-DL Audio API

An pythonic RESTful API for getting URL of YouTube videos with only audio or video+audio, perfect for playing in background reducing the network bandwith. Uses [youtube-dl][1] for the queries, and [Flask][2] for the web microframework.

## Requirements

The project requires Python 3.6 or higher, and install some dependencies.

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

The app can be scalated using `gunicorn -c gunicorn_config.py ytdl_audio_api.wsgi`. Is configured to use `gevent` for asynchronous serving.

You can deploy the app to [Heroku][4] or into a [Docker][3] environment.

> **Note**: by default it will use `2 * Cores + 1` workers. You can change this using the `WORKERS`
> environment variable. In Heroku this is mandatory, so add a "Config Var" called `WORKERS` and put
> a value of 1 or 2 (if using the free dyno).

## Example

We did [a demo page][5] for that.

Also, I have an [instance][6] running with a little example.

## RESTful API

The API is described in the [OpenApi Schema][oas] or in the `/oas.yaml`/`/swagger.yaml` of a deployed service. Use <https://editor.swagger.io>, <https://petstore.swagger.io> (filling the URL at the top) or any other Swagger UI instance to see the API and its documentation.

With the spec, you can also generate clients to talk to your own instance on to my public instance.

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
  [oas]: https://github.com/melchor629/youtubedl-audio-api/blob/master/ytdl_audio_api/oas.yaml
