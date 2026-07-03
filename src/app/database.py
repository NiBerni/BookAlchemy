"""Database connection and session management."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)

# In production, this URL comes from environment variables
# Using a local SQLite database for local development ease
DATABASE_URL = "sqlite:///./local_dev.db"

# Create the SQLAlchemy 2.1 Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True to see raw SQL queries in the terminal
    future=True,  # Enforce SQLAlchemy 2.0+ strict behavior
)

# Create a session factory
SessionFactory = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_session() -> Session:
    """Provides a transactional scope around a series of operations."""
    return SessionFactory()
