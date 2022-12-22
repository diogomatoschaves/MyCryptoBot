#!/bin/sh

cd $DIRECTORY/service/

echo "$BINANCE_API_KEY"

exec gunicorn --bind 0.0.0.0:"$PORT" --pythonpath /usr/src/app wsgi:app
