#!/bin/sh

exec gunicorn --bind 0.0.0.0:"$PORT" --pythonpath /usr/src/app wsgi:app
