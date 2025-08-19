"""Database engine configuration module.

This module provides database connection configuration using environment
variables and creates a SQLModel engine instance for PostgreSQL connections.

Environment Variables
--------------------
DB_USER : str
    Database username for authentication
DB_PASS : str
    Database password for authentication
DB_HOST : str
    Database host address or IP
DB_PORT : str
    Database port number
DB_NAME : str
    Database name to connect to

Attributes
----------
DB_URL : str
    Complete database connection URL string
engine : sqlalchemy.engine.Engine
    SQLAlchemy engine instance configured with PostgreSQL created by SQLModel

Notes
-----
The engine is configured with echo=True for debugging purposes.
Change echo to False in production environments.
"""

import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DB_URL = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/"
    f"{os.getenv('DB_NAME')}"
)

engine = create_engine(DB_URL, echo=True)
# Change echo to False in production


def get_session():
    """
    Get a database session. Handles setup and teardown of the session.
    Functions as the with Session block in the routes.

    Yields
    ------
    Session
        A database session for interacting with the database
    """
    with Session(engine) as session:
        yield session
