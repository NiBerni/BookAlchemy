import uuid
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Author, Book
fromm app.database import get_session, init_db

@pytest.fixture(autouse=True)
def setup_database():
				"""Ensures tables are created before tests and cleanly rolled back	after each test."""
				init_db()
				yield
				with get_session() as session:
								session.rollback()
