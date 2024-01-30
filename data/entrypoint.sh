#!/bin/sh

cd $DIRECTORY/service/ || exit

exec gunicorn wsgi:application \
--bind 0.0.0.0:"$PORT" \
--pythonpath /app \
--timeout 120
