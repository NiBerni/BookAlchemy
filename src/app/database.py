"""Database connection and session management."""

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

logger = logging.getLogger(__name__)


BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATA_DIR, 'library.sqlite3')}"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
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


def init_db() -> None:
    """Initializes database tables. Call this within the app factory."""
    from .models import Base

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at {DATABASE_URL}.")
