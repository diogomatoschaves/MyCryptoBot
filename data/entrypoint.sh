#!/bin/sh

cd $DIRECTORY/service/ || exit

exec gunicorn --bind 0.0.0.0:"$PORT" --pythonpath /app wsgi:application
