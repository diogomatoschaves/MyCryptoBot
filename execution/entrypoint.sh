#!/bin/sh

cd $DIRECTORY/service/

exec gunicorn wsgi:app \
--bind 0.0.0.0:"$PORT" \
--pythonpath /usr/src/app \
--timeout 120
