import json
import logging
import os
import sys
import time
from datetime import timedelta

from flask import Flask, send_from_directory
import django
from flask_cors import CORS

import redis
from flask_jwt_extended import JWTManager, create_access_token

from data.service.cron_jobs.app_health import check_app_health
from data.service.cron_jobs.main import start_background_scheduler
from shared.utils.settings import settings
from shared.utils.helpers import is_pipeline_loading, get_jwt_secret_key, LOADING

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data.service.blueprints.user_management import user_management
from data.service.blueprints.dashboard import dashboard
from data.service.blueprints.bots_api import start_symbol_trading, bots_api
from data.service.blueprints.proxy import proxy


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


from database.model.models import Pipeline
from shared.utils.logger import configure_logger


configure_logger(settings.logger_level)

cache = redis.from_url(settings.redis_url)

# Internal service token: bounded lifetime + periodic rotation so a leaked
# token can't be used indefinitely. The TTL is comfortably longer than any
# job's lifetime, so in-flight RQ jobs (which carry a token captured at
# enqueue time) never fail mid-flight.
SERVICE_TOKEN_TTL = timedelta(hours=24)
SERVICE_TOKEN_REFRESH_HOURS = 12


def set_service_token(app):
    with app.app_context():
        access_token = create_access_token(
            identity='data-service', expires_delta=SERVICE_TOKEN_TTL
        )
        cache.set("service_bearer_token", f"Bearer {access_token}")


def startup_task(app):

    cache.set(LOADING, json.dumps([]))

    set_service_token(app)

    start_background_scheduler(
        token_refresher=lambda: set_service_token(app),
        refresh_hours=SERVICE_TOKEN_REFRESH_HOURS,
    )

    active_pipelines = Pipeline.objects.filter(active=True)

    for pipeline in active_pipelines:
        response = start_symbol_trading(pipeline, restart=True)

        if not response["success"]:
            logging.info(f"Pipeline {pipeline.id} could not be started. {response['message']}")

    while any(is_pipeline_loading(cache, pipeline.id) for pipeline in active_pipelines):
        time.sleep(10)

    check_app_health()


def create_app():

    app = Flask(__name__, static_folder="../build/static", template_folder="../build")
    app.debug = False

    app.register_blueprint(bots_api, url_prefix='/api')
    app.register_blueprint(dashboard, url_prefix='/api')
    app.register_blueprint(user_management, url_prefix='/api')
    app.register_blueprint(proxy, url_prefix='/api')

    app.config["JWT_SECRET_KEY"] = get_jwt_secret_key()
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=settings.token_expires_days)

    JWTManager(app)

    CORS(app, origins=os.getenv("CORS_ALLOWED_ORIGINS", "*").split(","))

    startup_task(app)

    @app.get('/', defaults={'path': ''})
    @app.get('/<path:path>')
    def index(path):

        build_dir = os.path.abspath("../build")
        static_dir = os.path.abspath("../build/static")

        if path != "" and os.path.exists(os.path.join(build_dir, path)):
            return send_from_directory(build_dir, path)
        elif path != "" and os.path.exists(os.path.join(static_dir, path)):
            return send_from_directory(static_dir, path)
        else:
            if os.path.exists(os.path.join(build_dir, 'index.html')):
                return send_from_directory(build_dir, 'index.html')
            else:
                return "No files found!"

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host='0.0.0.0')
