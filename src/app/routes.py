import logging
import uuid
from datetime import datetime

from flask import (
    Blueprint,
    Response,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import select

from .database import get_session
from .decorators import handle_api_errors
from .models import Author, Book

logger = logging.getLogger(__name__)
bp = Blueprint("main", __name__)


@bp.route("/health")
@handle_api_errors
def health_check() -> tuple[Response, int]:
    """
    Simple health check endpoint.
    Mandatory to check the availability of the Docker-Container.
    """
    payload = {"status": "ok", "message": "The Python 3.14 Flask Container is running"}
    return jsonify(payload), 200


@bp.route("/", methods=["GET"])
@handle_api_errors
def home() -> Response | str:
    """Fetches books, handles sorting and constructs the cover image URL."""
    sort_by = request.args.get("sort_by", "title")
    search_query = request.args.get("search", "").strip()

    with get_session() as session:
        if search_query:
            books_raw = Book.search_by_keyword_secure(session, search_query)
        else:
            if sort_by == "author":
                query = select(Book).join(Author).order_by(Author.name)
            else:
                query = select(Book).order_by(Book.title)
            books_raw = session.execute(query).scalars().all()

        books_data = []
        for book in books_raw:
            books_data.append(
                {
                    "title": book.title,
                    "author_name": book.author.name,
                    "publication_year": book.publication_year,
                    "cover_url": f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg",
                }
            )
    return render_template(
        "home.html", books=books_data, current_sort=sort_by, search_query=search_query
    )


@bp.route("/add_author", methods=["GET", "POST"])
@handle_api_errors
def add_author() -> Response | str:
    """Handles the creation of a new author."""
    if request.method == "POST":
        name = request.form.get("name")
        birth_date_str = request.form.get("birth_date")
        date_of_death_str = request.form.get("date_of_death")

        try:
            birth_date = (
                datetime.strptime(birth_date_str, "%Y-%m-%d").date()
                if birth_date_str
                else None
            )
            date_of_death = (
                datetime.strptime(date_of_death_str, "%Y-%m-%d").date()
                if date_of_death_str
                else None
            )

            with get_session() as session:
                new_author = Author(
                    name=name, birth_date=birth_date, date_of_death=date_of_death
                )
                session.add(new_author)
                session.commit()
            flash(f"Author '{name}' added successfully!", "success")
            return redirect(url_for("main.home"))

        except ValueError:
            flash("Invalid date format. Please use YYYY-MM-DD.", "error")
            return redirect(url_for("main.add_author"))
        except Exception as e:
            logger.error(f"Error adding author: {e}", exc_info=True)
            flash("An error occurred while adding the author.", "error")
            return redirect(url_for("main.add_author"))

    return render_template("add_author.html")


@bp.route("/add_book", methods=["GET", "POST"])
@handle_api_errors
def add_book() -> Response | str:
    """Handles the creation of a new book."""
    if request.method == "POST":
        title = request.form.get("title")
        isbn = request.form.get("isbn")
        publication_year_str = request.form.get("publication_year")
        author_id_str = request.form.get("author_id")

        # Guard clause: Ensure no fields are empty or None
        if not title or not isbn or not publication_year_str or not author_id_str:
            flash("All fields are required!", "error")
            return redirect(url_for("main.add_book"))

        try:
            pub_year = int(publication_year_str)
            author_id = uuid.UUID(str(author_id_str))

            with get_session() as session:
                new_book = Book(
                    title=title,
                    isbn=isbn,
                    publication_year=pub_year,
                    author_id=author_id,
                )
                session.add(new_book)
                session.commit()

            flash(f"Book '{new_book.title}' added successfully!", "success")
            return redirect(url_for("main.home"))

        except ValueError:
            logger.warning("Invalid publication year or author_id.")
            flash("Invalid data format. Please check your inputs.", "error")
            return redirect(url_for("main.add_book"))

        except Exception as e:
            logger.error(f"Error adding book: {e}", exc_info=True)
            flash("An error occurred while adding the book.", "error")
            return redirect(url_for("main.add_book"))

    with get_session() as session:
        # Assumes 'select' is imported at the top of the file
        authors = session.execute(select(Author).order_by(Author.name)).scalars().all()

    return render_template("add_book.html", authors=authors)


@bp.route("/book/<uuid:book_id>/delete", methods=["POST"])
@handle_api_errors
def delete_book(book_id: uuid.UUID) -> Response | str:
    """Handles the deletion of a book."""
    with get_session() as session:
        book = session.get(Book, book_id)
        if not book:
            flash(" 404 Book not found.", "error")
            return redirect(url_for("main.home"))

        title = book.title
        author = book.author

        session.delete(book)
        session.flush()

        remaining_books = (
            session.execute(select(Book).where(Book.author_id == author.id))
            .scalars()
            .first()
        )

        if not remaining_books:
            session.delete(author)
            logger.info(
                f'Deleted author "{author.name}" as they have no remaining books.'
            )
        session.commit()

    flash(
        f"Book '{title}' and its author '{author.name}' deleted successfully!",
        "success",
    )
    return redirect(url_for("main.home"))
