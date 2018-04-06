FROM python:3

RUN mkdir -p /opt/yt-audio-api
COPY requirements.txt /opt/yt-audio-api/
RUN pip install --no-cache-dir -r /opt/yt-audio-api/requirements.txt
COPY gunicorn.conf /opt/yt-audio-api/
COPY ytdl_audio_api /opt/yt-audio-api/

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
ENTRYPOINT gunicorn -c gunicorn.conf ytdl_audio_api.wsgi
