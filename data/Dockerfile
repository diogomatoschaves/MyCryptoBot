FROM python:slim

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

ENV DIRECTORY data

# Install and setup poetry
RUN pip install -U pip \
    && apt-get update \
    && yes | apt-get install libpq-dev \
    && apt install -y curl netcat \
    && curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python \
    && pip install psycopg2-binary==2.8.6
ENV PATH="${PATH}:/root/.poetry/bin"

COPY $DIRECTORY/poetry.lock $DIRECTORY/pyproject.toml /

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

WORKDIR /usr/src/app

COPY ./database/ ./database/
COPY ./$DIRECTORY/ ./$DIRECTORY/
COPY ./shared/ ./shared/

RUN useradd -m myuser
USER myuser

CMD bash /usr/src/app/$DIRECTORY/entrypoint.sh
