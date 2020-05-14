FROM python:3-alpine

WORKDIR /opt/yt-audio-api

COPY ./requirements.txt ./

RUN apk add --no-cache git build-base libffi-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del --no-cache git build-base libffi-dev && \
    rm -rf /root/.cache

COPY ./gunicorn_config.py ./
COPY ./ytdl_audio_api/ ./ytdl_audio_api/

ENV PORT 5000
EXPOSE 5000

CMD [ "gunicorn", "-c", "gunicorn_config.py", "ytdl_audio_api.wsgi" ]
