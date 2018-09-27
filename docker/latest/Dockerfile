FROM python:3

RUN mkdir -p /opt/yt-audio-api && \
    git clone https://github.com/melchor629/youtubedl-audio-api && \
    cd youtubedl-audio-api && \
    pip install --no-cache-dir -r requirements.txt && \
    cp -r ytdl_audio_api /opt/yt-audio-api && \
    cp gunicorn.conf /opt/yt-audio-api && \
    cd .. && \
    rm -r youtubedl-audio-api

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
CMD [ "gunicorn", "-c", "gunicorn.conf", "ytdl_audio_api.wsgi" ]
