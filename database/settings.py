import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.getenv("TEST", False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': 'db',
            'PORT': '5432',
            'CONN_MAX_AGE': 500
        }
    }

# Heroku: Update database configuration from $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

INSTALLED_APPS = (
    'database.model',
    'django.contrib.auth',
    'django.contrib.contenttypes'
)

SECRET_KEY = os.getenv('SECRET_KEY')

USE_TZ = True

AUTH_USER_MODEL = 'model.User'
