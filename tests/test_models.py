import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.database import get_session
from app.models import Author, Book


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
        assert author.books[0].title == "Harry Potter and the Sorcerer's Stone"


def test_defensive_book_requires_author():
    """Ensures database integrity - rejects Book creation without an associated Author"""
    with get_session() as session:
        orphan_book = Book(title="Orphaned Book")
        session.add(orphan_book)

        with pytest.raises(IntegrityError):
            session.commit()


def test_pep750_tstring_raw_query():
    """Verify that PEP 750 t-string implementation securely fetches data."""
    with get_session() as session:
        author = Author(name="Isaac Asimov")
        Book(title="Foundation", author=author)
        session.add(author)
        session.commit()

        results = Book.find_by_title_secure(session, "Foundation")
        assert len(results) == 1
        assert results[0].title == "Foundation"


def test_pep750_tstring_prevents_sql_injection():
    """Verify that t-strings neutralize malicious SQL injection attempts."""
    with get_session() as session:
        author = Author(name="Isaac Asimov")
        book = Book(title="Foundation", author=author)
        session.add(author)
        session.add(book)
        session.commit()

        malicious_injection = "Foundation' OR '1'='1 "

        results = Book.find_by_title_secure(session, malicious_injection)
        assert len(results) == 0

        results = Book.find_by_title_secure(session, "Foundation' OR '1'='1")
        assert len(results) == 0
