#!/bin/sh

cd $DIRECTORY/service/ || exit

echo "$EXECUTION_APP_URL"

exec gunicorn --bind 0.0.0.0:"$PORT" --pythonpath /app wsgi:application
