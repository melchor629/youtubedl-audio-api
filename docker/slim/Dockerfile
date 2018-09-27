FROM python:3-slim

RUN mkdir -p /opt/yt-audio-api && \
    apt-get update && apt-get install -y git && \
    git clone https://github.com/melchor629/youtubedl-audio-api && \
    cd youtubedl-audio-api && \
    pip install --no-cache-dir -r requirements.txt && \
    cp -r ytdl_audio_api /opt/yt-audio-api && \
    cp gunicorn.conf /opt/yt-audio-api && \
    cd .. && \
    rm -r youtubedl-audio-api && \
    apt-get purge -y git && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/*

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
CMD [ "gunicorn", "-c", "gunicorn.conf", "ytdl_audio_api.wsgi" ]
