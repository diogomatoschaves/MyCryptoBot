#!/bin/sh

cd data/service/

exec gunicorn --bind 0.0.0.0:"$PORT" wsgi:app
