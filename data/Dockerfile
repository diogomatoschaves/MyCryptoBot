FROM --platform=linux/amd64 node:13.12.0-alpine as build-step
ENV DIRECTORY dashboard

WORKDIR /app

COPY $DIRECTORY/package*.json ./
RUN npm clean-install


COPY ./$DIRECTORY/ ./

RUN npm run build


FROM --platform=linux/amd64 python:3.8-slim

ARG BINANCE_API_KEY
ARG BINANCE_API_SECRET
ARG BINANCE_API_KEY_TEST
ARG BINANCE_API_SECRET_TEST
ARG MODEL_APP_URL
ARG EXECUTION_APP_URL
ARG APP_NAME
ARG SECRET_KEY

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

USER root

COPY ./database/ ./app/database/
COPY ./$DIRECTORY/ ./app/$DIRECTORY/
COPY ./shared/ ./app/shared/

COPY --from=build-step app/build/. ./app/$DIRECTORY/build

WORKDIR /app

ENV BINANCE_API_KEY=$BINANCE_API_KEY
ENV BINANCE_API_SECRET=$BINANCE_API_SECRET
ENV BINANCE_API_KEY_TEST=$BINANCE_API_KEY_TEST
ENV BINANCE_API_SECRET_TEST=$BINANCE_API_SECRET_TEST
ENV MODEL_APP_URL=$MODEL_APP_URL
ENV EXECUTION_APP_URL=$EXECUTION_APP_URL
ENV APP_NAME=$APP_NAME
ENV SECRET_KEY=$SECRET_KEY

CMD bash $DIRECTORY/entrypoint.sh
