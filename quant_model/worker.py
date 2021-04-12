import os
import sys

module_path = os.path.abspath(os.path.join('../data'))
if module_path not in sys.path:
    sys.path.append(module_path)

import redis
from rq import Worker, Queue, Connection
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

listen = ['default']

redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
