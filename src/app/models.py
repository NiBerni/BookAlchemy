import uuid
from typing import Any, List

from sqlalchemy import ForeignKey, String, Uuid
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
    books: Mapped[List["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )


class Book(Base):
    """Represents a Book entity in the database."""

    __tablename__ = "books"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("authors.id"), nullable=False
    )
    author: Mapped["Author"] = relationship(back_populates="books")

    @classmethod
    def find_by_title_secure(cls, session: Any, search_title: str) -> List["Book"]:
        """Find books by title using parameterized queries to prevent SQL injection."""
        from sqlalchemy import tstring

        # 🚨 NEVER use f-strings here! Using PEP 750 t-strings (t"...")
        # securely binds the variable at the database driver level.
        query = tstring(t"SELECT * FROM books WHERE title = {search_title}")
        result = session.execute(query)
        return result.scalars().all()
