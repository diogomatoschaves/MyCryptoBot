import os
import sys
from datetime import timedelta

from flask import Flask, send_from_directory
import django
from flask_cors import CORS

import redis
from flask_jwt_extended import JWTManager, create_access_token

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from data.service.blueprints.user_management import user_management
from data.service.blueprints.dashboard import dashboard
from data.service.blueprints.bots_api import start_symbol_trading, bots_api
from data.service.blueprints.proxy import proxy


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "database.settings")
django.setup()


from database.model.models import Position
from shared.utils.logger import configure_logger

configure_logger(os.getenv("LOGGER_LEVEL", "INFO"))

cache = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))


def startup_task(app):

    open_positions = Position.objects.filter(open=True)

    with app.app_context():
        access_token = create_access_token(identity='abc', expires_delta=False)
        bearer_token = 'Bearer ' + access_token
        cache.set("bearer_token", bearer_token)

    for open_position in open_positions:

        start_symbol_trading(open_position.pipeline)
        open_position.pipeline.active = True
        open_position.pipeline.save()


def create_app():
    app = Flask(__name__, static_folder="../build/static", template_folder="../build")
    app.debug = False

    app.register_blueprint(bots_api, url_prefix='/api')
    app.register_blueprint(dashboard, url_prefix='/api')
    app.register_blueprint(user_management, url_prefix='/api')
    app.register_blueprint(proxy, url_prefix='/api')

    app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=3)

    jwt = JWTManager(app)

    CORS(app)

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
