"""
Application factory to construct a configured Flask instance.

This function creates and configures a Flask application. It initializes the database and registers the routes.
"""

from typing import Any, Mapping, Optional

from flask import Flask

from .database import init_db


def create_app(test_config: Optional[Mapping[str, Any]] = None) -> Flask:
    """
    Create a Flask application instance.

    This function initializes a new Flask application and configures it based on the provided test configuration. If no test configuration is provided, it uses default settings for development purposes.

    :param test_config: An optional dictionary containing test-specific configurations.
    :type test_config: Optional[Mapping[str, Any]]

    :return: A configured Flask application instance.
    :rtype: Flask
    """
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY="replace-with-a-secure-environment-variable",
        )
    else:
        app.config.from_mapping(test_config)
    from . import models  # noqa: F401, PLC0415

    with app.app_context():
        init_db()

    from . import routes

    app.register_blueprint(routes.bp)

    return app
