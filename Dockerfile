FROM python:alpine

RUN mkdir -p /opt/yt-audio-api
COPY requirements.txt /opt/yt-audio-api/
RUN pip install -r /opt/yt-audio-api/requirements.txt
COPY app.py decorator.py logger.py ytdl.py /opt/yt-audio-api/

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
ENTRYPOINT python app.py
