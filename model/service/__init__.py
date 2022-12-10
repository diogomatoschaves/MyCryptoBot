import os

import model.service.app as application


def create_app(testing=False, env_vars=None):
    """Create and configure an instance of the Flask application."""

    if env_vars is not None:
        for key, value in env_vars.items():
            os.environ.setdefault(key, value)

    app = application.create_app()

    app.config['TESTING'] = testing

    return app
