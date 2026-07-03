from flask import Blueprint, Response, jsonify

from .decorators import handle_api_errors

bp = Blueprint("main", __name__)


@bp.route("/")
@handle_api_errors
def health_check() -> tuple[Response, int]:
    """
    Simple healthcheck endpoint.
    Nice to check the availability of the Docker-Container.
    """
    payload = {"status": "ok", "message": "The Python 3.14 Flask Container is running"}
    return jsonify(payload), 200
