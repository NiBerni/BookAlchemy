"""
Module to manage database sessions and initialize the database schema.

This module provides functions to create a new database session and initialize the database schema. It uses SQLAlchemy for ORM operations.
"""

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
    """
    Create a new database session.

    :return: A SQLAlchemy session object.
    :rtype: Session
    """
    return SessionFactory()


def init_db() -> None:
    """Initialize the database schema.

    Create all tables defined in the models module using the provided engine.
    This function ensures that the database is properly set up with the necessary tables
    and logs the initialization URL for verification purposes.

    :raises Exception: If an error occurs during the creation of the tables.
    """
    from .models import Base

    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized at {DATABASE_URL}.")
