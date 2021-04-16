import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import dj_database_url


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
            'NAME': 'crypto_bot',
            'USER': 'postgres',
            'PASSWORD': '6730',
            'HOST': 'localhost',
            'PORT': '5432',
            'CONN_MAX_AGE': 500
        }
    }

# Heroku: Update database configuration from $DATABASE_URL.
db_from_env = dj_database_url.config(conn_max_age=500)
DATABASES['default'].update(db_from_env)

INSTALLED_APPS = (
    'database.model',
)

# SECURITY WARNING: Modify this secret key if using in production!
SECRET_KEY = '6few3nci_q_o@l1dlbk81%wcxe!*6r29yu629&d97!hiqat9fa'

USE_TZ = True
