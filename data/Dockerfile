FROM --platform=linux/amd64 node:20-alpine as build-step
ENV DIRECTORY dashboard

WORKDIR /app

COPY $DIRECTORY/package*.json ./
RUN npm clean-install


COPY ./$DIRECTORY/ ./

RUN npm run build


FROM --platform=linux/amd64 python:3.8-slim

# Secrets and app config are injected at runtime (Heroku config vars /
# compose env_file) — never as build args, which persist in image layers.

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

ENV DIRECTORY data

ENV POETRY_HOME /opt/poetry

# Install and setup poetry
RUN pip install -U pip \
    && apt-get update \
    && yes | apt-get install libpq-dev \
    && apt install -y curl netcat-traditional \
    && curl -sSL https://install.python-poetry.org | python - --version 1.7.1 \
    && pip install psycopg2-binary==2.8.6
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY $DIRECTORY/poetry.lock $DIRECTORY/pyproject.toml /

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --only main

COPY ./proj.conf ./app/$DIRECTORY/service/
COPY ./database/ ./app/database/
COPY ./$DIRECTORY/ ./app/$DIRECTORY/
COPY ./shared/ ./app/shared/

COPY --from=build-step app/dist/. ./app/$DIRECTORY/build

WORKDIR /app

# run as a non-root user (mirrors the model/execution images)
RUN useradd -m myuser
USER myuser

CMD bash $DIRECTORY/entrypoint.sh
