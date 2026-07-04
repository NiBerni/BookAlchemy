import logging
from functools import wraps
from typing import Any, Callable

from flask import jsonify
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)


def handle_api_errors(func: Callable) -> Callable:
    """
    Decorator to handle API errors and provide a standardized JSON response.

    This decorator wraps any function that may raise an exception, catching both `HTTPException` for HTTP-specific errors and general exceptions for internal server errors. It logs the error details for critical issues and returns a JSON response with an appropriate error message and status code.

    :param func: The function to be decorated.
    :type func: Callable
    :return: The wrapped function.
    :rtype: Callable

    :raises HTTPException: If the original function raises an `HTTPException`, it is caught and handled by returning a JSON response with the exception's name and description.
    :raises Exception: For any other exceptions, the error is logged as a critical issue, and a JSON response with a generic "Internal Server Error" message and status code 500 is returned.
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
