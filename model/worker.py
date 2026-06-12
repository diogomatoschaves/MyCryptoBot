import os

import redis
from dotenv import find_dotenv, load_dotenv
from rq import Worker, Queue, Connection
import django

from model.service.cloud_storage import cloud_storage_startup
from shared.utils.settings import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

listen = ['default']


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

cloud_storage_startup()

redis_url = settings.redis_url

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
