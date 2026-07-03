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

def test_create_author_and_book():
	"""Test the creation of an Author and assosiated Book with UUIDs"""
	with get_session() as session:
		author = Author(name="J.K. Rowling")
		book = Book(title="Harry Potter and the Sorcerer's Stone", author=author)
		session.add(author)
		session.commit()

		assert isinstance(author.id, uuid.UUID)
		assert isinstance(book.id, uuid.UUID)
		assert len(author.books) == 1
		assert.author.books[0] == "Harry Potter and the Sorcerer's Stone"

def test_defensive_book_requires_author():
	"""Ensures database integrity - rejects Book creation without an associated Author"""
	with get_session() as session:
		orphan_book = Book(title="Orphaned Book")
		session.add(orphan_book)

		with pytest.raises(IntegrityError):
			session.commit()
