FROM python:alpine

RUN mkdir -p /opt/yt-audio-api/templates
COPY app.py decorator.py logger.py requirements.txt ytdl.py /opt/yt-audio-api/
COPY templates/index.html /opt/yt-audio-api/templates/index.html
RUN pip install -r /opt/yt-audio-api/requirements.txt

ENV PORT 5000
EXPOSE 5000

WORKDIR /opt/yt-audio-api/
ENTRYPOINT python app.py
