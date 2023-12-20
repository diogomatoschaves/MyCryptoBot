FROM --platform=linux/amd64 python:3.8-slim

ARG BINANCE_API_KEY
ARG BINANCE_API_SECRET
ARG BINANCE_API_KEY_TEST
ARG BINANCE_API_SECRET_TEST
ARG APP_NAME
ARG SECRET_KEY

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

ENV DIRECTORY execution

ENV POETRY_HOME /opt/poetry

# Install and setup poetry
RUN pip install -U pip \
    && apt-get update \
    && yes | apt-get install libpq-dev \
    && apt install -y curl netcat-traditional \
    && curl -sSL https://install.python-poetry.org | python - --version 1.2.0 \
    && pip install psycopg2-binary==2.8.6
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY $DIRECTORY/poetry.lock $DIRECTORY/pyproject.toml /

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-dev

WORKDIR /usr/src/app

COPY ./proj.conf ./
COPY ./database/ ./database/
COPY ./$DIRECTORY/ ./$DIRECTORY/
COPY ./shared/ ./shared/

RUN useradd -m myuser
USER myuser

ENV BINANCE_API_KEY=$BINANCE_API_KEY
ENV BINANCE_API_SECRET=$BINANCE_API_SECRET
ENV BINANCE_API_KEY_TEST=$BINANCE_API_KEY_TEST
ENV BINANCE_API_SECRET_TEST=$BINANCE_API_SECRET_TEST
ENV APP_NAME=$APP_NAME
ENV SECRET_KEY=$SECRET_KEY

CMD bash /usr/src/app/$DIRECTORY/entrypoint.sh
