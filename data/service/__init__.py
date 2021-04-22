import os

import data.service.app as application


def create_app(testing=False, env_vars=None):
    """Create and configure an instance of the Flask application."""

    if env_vars is not None:
        for key, value in env_vars.items():
            os.environ.setdefault(key, value)

    application.app.config['TESTING'] = testing

    return application.app
