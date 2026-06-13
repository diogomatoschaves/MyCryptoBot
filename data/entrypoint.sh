#!/bin/sh

cd $DIRECTORY/service/ || exit

# IMPORTANT: must stay at a single worker - startup restarts active pipelines
# and the data-collection instances live in process memory; a second worker
# would double-start every bot. Concurrency (incl. long-lived SSE streams on
# /api/events) comes from threads instead.
exec gunicorn wsgi:application \
--bind 0.0.0.0:"$PORT" \
--pythonpath /app \
--worker-class gthread \
--threads 8 \
--timeout 120
