import uuid
from datetime import date
from typing import Any, List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 declarative models."""

    pass


class Author(Base):
    """Represents an Author entity in the database."""

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
    """Represents a Book entity in the database."""

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
        """Find books by title using parameterized queries to prevent SQL injection."""
        from sqlalchemy import select, tstring

        # 🚨 NEVER use f-strings here! Using PEP 750 t-strings (t"...")
        # securely binds the variable at the database driver level.
        raw_query = tstring(t"SELECT * FROM books WHERE title = {search_title}")
        orm_query = select(cls).from_statement(raw_query)
        result = session.execute(orm_query)
        return list(result.scalars().all())
