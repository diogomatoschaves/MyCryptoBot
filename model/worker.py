import os

import redis
from dotenv import find_dotenv, load_dotenv
from rq import Worker, Queue, Connection
import django

from model.service.cloud_storage import cloud_storage_startup
from shared.utils.config_parser import get_config

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()

listen = ['default']

config_vars = get_config('model')

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

cloud_storage_startup()

redis_url = os.getenv('REDIS_URL', config_vars.redis_url)

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
