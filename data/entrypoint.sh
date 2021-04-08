#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$SQL_HOST" "$SQL_PORT"; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python database/manage.py migrate

cd data/service/

exec gunicorn --bind 0.0.0.0:"$PORT" wsgi:app
