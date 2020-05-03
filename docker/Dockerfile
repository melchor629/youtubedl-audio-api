FROM python:3-alpine

RUN mkdir -p /opt/yt-audio-api && \
    apk add --no-cache git build-base libffi-dev && \
    git clone https://github.com/melchor629/youtubedl-audio-api && \
    cd youtubedl-audio-api && \
    pip install --no-cache-dir -r requirements.txt && \
    cp -r ytdl_audio_api /opt/yt-audio-api && \
    cp gunicorn_config.py /opt/yt-audio-api && \
    cd .. && \
    rm -r youtubedl-audio-api && \
    apk del --no-cache git build-base libffi-dev

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
CMD [ "gunicorn", "-c", "gunicorn_config.py", "ytdl_audio_api.wsgi" ]
