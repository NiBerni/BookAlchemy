import uuid
from datetime import date
from typing import Any, List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 declarative models."""

    pass


class Author(Base):
    """
    Represents an author in the digital library database.

    This SQLAlchemy model maps to the 'authors' table. It stores details about a person
    who has written books, and establishes a one-to-many relationship with the `Book` model.

    :ivar id: Primary key. Unique identifier for the author, automatically generated as a UUID4.
    :vartype id: uuid.UUID
    :ivar name: The full name of the author. Maximum 150 characters and cannot be null.
    :vartype name: str
    :ivar birth_date: The date of birth of the author, if known.
    :vartype birth_date: datetime.date | None
    :ivar date_of_death: The date of death of the author, if applicable.
    :vartype date_of_death: datetime.date | None
    :ivar books: A list of associated Book objects. Deleting an author cascades to delete all their books.
    :vartype books: list["Book"]
    """

    __tablename__ = "authors"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    birth_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    date_of_death: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    books: Mapped[List["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f'<Author(id={self.id}, name="{self.name}")>'


class Book(Base):
    """
    Represents a book in the digital library database.

    This SQLAlchemy model maps to the 'books' table. It stores essential information
    about a book, including its unique ISBN, title, publication year, and establishes
    a many-to-one relationship with the `Author` model.

    :ivar id: Primary key. Unique identifier for the book, automatically generated as a UUID4.
    :vartype id: uuid.UUID
    :ivar isbn: The 13-character International Standard Book Number. Must be unique and cannot be null.
    :vartype isbn: str
    :ivar title: The full title of the book. Maximum 200 characters.
    :vartype title: str
    :ivar publication_year: The year the book was published.
    :vartype publication_year: int
    :ivar author_id: Foreign key referencing the author's UUID in the 'authors' table.
    :vartype author_id: uuid.UUID
    :ivar author: The related Author object, populated automatically via SQLAlchemy relationship.
    :vartype author: Author
    """

    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    isbn: Mapped[str] = mapped_column(String(13), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    publication_year: Mapped[int] = mapped_column(Integer, nullable=False)

    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("authors.id"), nullable=False
    )
    author: Mapped["Author"] = relationship(back_populates="books")

    def __str__(self) -> str:
        return f"{self.title} by {self.author.name}"

    def __repr__(self) -> str:
        return f'<Book(isbn={self.isbn}, title="{self.title}")>'

    @classmethod
    def find_by_title_secure(cls, session: Any, search_title: str) -> List["Book"]:
        """
        Execute a secure query to find books by title using parameterized SQL.

        :param session: SQLAlchemy session object used for database operations.
        :type session: Any
        :param search_title: Title of the book to search for.
        :type search_title: str
        :return: List of Book objects that match the given title.
        :rtype: List["Book"]
        """
        from sqlalchemy import select, tstring

        # 🚨 NEVER use f-strings here! Using PEP 750 t-strings (t"...")
        # securely binds the variable at the database driver level.
        raw_query = tstring(t"SELECT * FROM books WHERE title = {search_title}")
        orm_query = select(cls).from_statement(raw_query)
        result = session.execute(orm_query)
        return list(result.scalars().all())

    @classmethod
    def search_by_keyword_secure(cls, session: Any, keyword: str) -> List["Book"]:
        """
        Execute a secure search for books by keyword using parameterized query.

        :param session: Database session object.
        :type session: Any

        :param keyword: Search keyword to find in book titles.
        :type keyword: str

        :return: List of matching Book objects.
        :rtype: List["Book"]

        This method securely performs a database search for books with titles containing the specified keyword. It uses parameterized queries (t-strings) to prevent SQL injection attacks, ensuring that the search is both safe and efficient.
        """
        from sqlalchemy import select, tstring

        search_pattern = f"%{keyword}%"

        # 🚨 NEVER use f-strings here! Using PEP 750 t-strings (t"...")
        # securely binds the variable at the database driver level.

        raw_query = tstring(t"SELECT * FROM books WHERE title LIKE {search_pattern}")
        orm_query = select(cls).from_statement(raw_query)
        result = session.execute(orm_query)
        return list(result.scalars().all())
