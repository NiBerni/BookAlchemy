from typing import Any, Mapping, Optional

from flask import Flask

from .database import init_db


def create_app(test_config: Optional[Mapping[str, Any]] = None) -> Flask:
    """Application factory to construct a configured Flask instance."""
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY="replace-with-a-secure-environment-variable",
        )
    else:
        app.config.from_mapping(test_config)

    with app.app_context():
        init_db()

    from . import routes

    app.register_blueprint(routes.bp)

    return app
