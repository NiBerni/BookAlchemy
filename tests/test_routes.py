from datetime import date

import pytest
from flask.testing import FlaskClient

from app.database import engine, get_session
from app.models import Author, Base, Book


def test_health_check_success(client: FlaskClient) -> None:
    """Ensures the health check endpoint returns 200 OK and expected payload."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.get_json()
    assert data is not None
    assert data.get("status") == "ok"
    assert data.get("message") == "The Python 3.14 Flask Container is running"


def test_404_handling(client: FlaskClient) -> None:
    """Ensures that unknown routes are handled securely without exposing stack traces."""
    response = client.get("/invalid-route-that-does-not-exist")
    assert response.status_code == 404


def test_add_author_post(client: FlaskClient) -> None:
    """Test defensive creation of an author via POST request"""
    response = client.post(
        "/add_author",
        data={
            "name": "Frank Herbert",
            "birth_date": "1920-10-08",
            "date_of_death": "1986-02-11",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    with get_session() as session:
        from sqlalchemy import select

        author = session.execute(
            select(Author).where(Author.name == "Frank Herbert")
        ).scalar_one_or_none()
        assert author is not None
        assert author.birth_date == date(1920, 10, 8)
        assert author.date_of_death == date(1986, 2, 11)
        assert author.id is not None
        assert author.name == "Frank Herbert"


def test_add_book_post(client: FlaskClient) -> None:
    """Test defensive creation of a book linked to an existing author via POST request"""
    with get_session() as session:
        author = Author(name="George Orwell", birth_date=date(1903, 6, 25))
        session.add(author)
        session.commit()
        author_id = author.id

    response = client.post(
        "/add_book",
        data={
            "title": "1984",
            "isbn": "9780451524935",
            "publication_year": 1949,
            "author_id": str(author.id),
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    with get_session() as session:
        from sqlalchemy import select

        book = session.execute(
            select(Book).where(Book.isbn == "9780451524935")
        ).scalar_one_or_none()
        assert book is not None
        assert book.author_id == author.id
        assert book.id is not None
        assert book.title == "1984"


def test_home_page_sorting(client: FlaskClient) -> None:
    """Ensures the home page sorts books by title correctly."""
    with get_session() as session:
        author = Author(name="Author A")
        session.add_all(
            [
                Book(
                    title="Zebra Facts",
                    isbn="111",
                    publication_year=2000,
                    author=author,
                ),
                Book(
                    title="Apple Facts",
                    isbn="222",
                    publication_year=2001,
                    author=author,
                ),
            ]
        )
        session.commit()
    response = client.get("/?sort_by=title")
    html_content = response.data.decode("utf-8")
    assert html_content.find("Apple Facts") < html_content.find("Zebra Facts")
