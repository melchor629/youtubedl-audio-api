FROM python:3.14-alpine AS requirements

WORKDIR /app
RUN pip install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv requirements > requirements.txt


FROM python:3.14-alpine

WORKDIR /opt/yt-audio-api
COPY gunicorn_config.py ./
COPY --from=requirements /app/requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt
COPY ytdl_audio_api/ ./ytdl_audio_api/

ENV PORT 5000

CMD [ "gunicorn", "-c", "gunicorn_config.py", "ytdl_audio_api.wsgi" ]
