FROM python:3

RUN mkdir -p /opt/yt-audio-api/ytdl_audio_api
COPY requirements.txt gunicorn_config.py /opt/yt-audio-api/
RUN pip install --no-cache-dir -r /opt/yt-audio-api/requirements.txt
COPY ytdl_audio_api /opt/yt-audio-api/ytdl_audio_api

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
CMD [ "gunicorn", "-c", "gunicorn_config.py", "ytdl_audio_api.wsgi" ]
