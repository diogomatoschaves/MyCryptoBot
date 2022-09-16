FROM python:3.8-slim

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
    && apt install -y curl netcat \
    && curl -sSL https://install.python-poetry.org | python - --version 1.2.0 \
    && pip install psycopg2-binary==2.8.6
ENV PATH="$POETRY_HOME/bin:$PATH"

COPY $DIRECTORY/poetry.lock $DIRECTORY/pyproject.toml /

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-dev

WORKDIR /usr/src/app

COPY ./database/ ./database/
COPY ./$DIRECTORY/ ./$DIRECTORY/
COPY ./shared/ ./shared/

RUN useradd -m myuser
USER myuser

CMD bash /usr/src/app/$DIRECTORY/entrypoint.sh
