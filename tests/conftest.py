import pytest
from flask import Flask
from flask.testing import FlaskClient

from src.app import create_app


@pytest.fixture
def app() -> Flask:
    """Creates a fresh, isolated instance of the Flask app for testing."""
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Provides a test client for the application."""
    return app.test_client()
