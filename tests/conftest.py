import os

import pytest
from flask import Flask
from flask.testing import FlaskClient

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app
from app.database import engine
from app.models import Base


@pytest.fixture
def app() -> Flask:
    """Creates a fresh, isolated instance of the Flask app for testing."""
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Provides a test client for the application."""
    return app.test_client()


@pytest.fixture(autouse=True)
def setup_database():
    """Ensures tables are created before tests and cleanly rolled back	after each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

    Base.metadata.drop_all(bind=engine)
