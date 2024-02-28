import data.service.app as application


def create_app(testing=False):
    """Create and configure an instance of the Flask application."""

    app = application.create_app()

    app.config['TESTING'] = testing

    return app
