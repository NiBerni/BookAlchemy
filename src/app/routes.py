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
    Returns the current status of the application.

    :rtype: Tuple[Response, int]
    """
    payload = {"status": "ok", "message": "The Python 3.14 Flask Container is running"}
    return jsonify(payload), 200


@bp.route("/", methods=["GET"])
@handle_api_errors
def home() -> Response | str:
    """
    Renders the home page with a list of books.

    :param sort_by: The field by which to sort the books. Default is 'title'.
    :type sort_by: str
    :param search_query: The keyword to search for in book titles.
    :type search_query: str
    :return: A rendered template containing the home page and book data.
    :rtype: Response | str
    """
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
    """
    Handles the creation of a new author via a web form.

    GET: Renders the author creation form.
    POST: Validates the form input, parses optional birth and death dates
    (expected in YYYY-MM-DD format), and saves the new author to the database.

    :return: A redirect to the homepage on success, or the rendered HTML template
             with flashed error messages on failure or for GET requests.
    :rtype: Response | str
    """
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
    """
    Execute the route to add a new book.

    Handles both GET and POST requests.
    If the request method is POST, it processes the form data, validates inputs, creates a new `Book` object,
    and adds it to the database. On successful addition, it redirects to the home page with a success message.
    If any errors occur (such as invalid publication year or author ID), it logs the error, flashes an error message,
    and redirects back to the book add page.

    If the request method is GET, it retrieves all authors from the database and renders
    the `add_book.html` template, passing the list of authors to the template.
    """
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
    """

    Delete a book by its UUID.

    :param book_id: The UUID of the book to delete.
    :type book_id: uuid.UUID

    :return: A success message if the book is deleted, or an error message if the book is not found.
    :rtype: str | Response

    .. note::
        This function deletes both the book and the associated author if it no longer has any books.
    """
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
