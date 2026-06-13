import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url
from dotenv import find_dotenv, load_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if os.getenv("TEST"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_DB'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': 'localhost',
            'PORT': '5433',
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

if not SECRET_KEY:
    if os.getenv("TEST"):
        SECRET_KEY = 'insecure-test-only-secret-key'
    else:
        raise EnvironmentError("SECRET_KEY environment variable must be set")

# Pin the implicit primary key type to what the existing schema already uses;
# switching to BigAutoField would require migrating every table's PK to bigint.
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

USE_TZ = True

AUTH_USER_MODEL = 'model.User'
