import logging
from functools import wraps
from typing import Any, Callable

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def handle_api_errors(func: Callable) -> Callable:
    """
    Custom decorator to gracefully catch unexpected errors,
    preventing sensitive stack trace leaks to the client.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except HTTPException as http_exc:
            return jsonify(
                {"error": http_exc.name, "description": http_exc.description}
            ), http_exc.code
        except Exception as exc:
            # Standard f-string used for standard logging interpolation
            logger.error(
                f"Critical unhandled exception in {func.__name__}: {exc}", exc_info=True
            )
            return jsonify({"error": "Internal Server Error"}), 500

    return wrapper
