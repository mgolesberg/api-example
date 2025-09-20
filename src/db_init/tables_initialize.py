"""Database table initialization and test data setup module.

This module provides functions for creating database tables and populating
them with test data. It's designed for development and testing purposes
to set up a complete database environment.

Functions
---------
create_tables : None
    Create all database tables defined in the models
initialize_test_data : None
    Initialize test data in the database for all tables
"""

from sqlmodel import SQLModel, Session
from sqlalchemy.engine import Engine
from sqlalchemy import text
from src.db import models
from src.db_init import example_data
from src.db.db import engine, get_session


def drop_all_tables(db_engine: Engine):
    """Drop all database tables and custom types in the correct order.

    This function drops tables in dependency order (child tables first,
    then parent tables) and also drops custom enum types that persist
    even after tables are dropped.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        The SQLAlchemy engine instance to use for dropping tables
    """
    SQLModel.metadata.drop_all(db_engine)

    with db_engine.connect() as conn:
        conn.execute(text("DROP TYPE IF EXISTS orderstatus CASCADE"))
        conn.execute(text("DROP TYPE IF EXISTS conditionenum CASCADE"))
        conn.commit()


def create_tables(db_engine: Engine):
    """Create all database tables defined in the models.

    Parameters
    ----------
    engine : sqlalchemy.engine.Engine
        The SQLAlchemy engine instance to use for creating tables
    """
    SQLModel.metadata.create_all(db_engine)


def initialize_test_data(session: Session):
    """Initialize test data in the database.

    This function creates test data for all tables:
    - Users
    - Interests
    - Dislikes
    - Allergies (predefined list)
    - UserAllergies (many-to-many relationships)
    - Products
    - Orders
    - Purchases

    Parameters
    ----------
    session : sqlmodel.Session
        The SQLModel session to use for creating test data

    Notes
    -----
    This function creates test data for all tables:
    - Users
    - Interests
    - Dislikes
    - Allergies (predefined list)
    - UserAllergies (many-to-many relationships)
    - Products
    - Orders
    - Purchases
    """
    for user in example_data.TEST_USERS:
        session.add(models.User(**user))
    for allergy in example_data.TEST_ALLERGIES:
        session.add(models.Allergy(**allergy))
    session.commit()
    for interest in example_data.TEST_INTERESTS:
        session.add(models.Interest(**interest))
    for dislike in example_data.TEST_DISLIKES:
        session.add(models.Dislike(**dislike))
    for user_allergy in example_data.TEST_USER_ALLERGIES:
        session.add(models.UserAllergy(**user_allergy))
    for product in example_data.TEST_PRODUCTS:
        session.add(models.Product(**product))
    for order in example_data.TEST_ORDERS:
        session.add(models.Order(**order))
    for purchase in example_data.TEST_PURCHASES:
        session.add(models.Purchase(**purchase))

    session.commit()


def main():
    """Main function to initialize database tables and test data.

    This function orchestrates the complete database setup process:
    1. Drops existing tables (if any)
    2. Creates new tables based on current models
    3. Populates tables with test data

    Raises
    ------
    Exception
        If there's an error during database initialization
    """
    drop_all_tables(engine)

    create_tables(engine)

    session_gen = get_session()
    session = next(session_gen)
    try:
        initialize_test_data(session)
    except Exception as e:
        session.rollback()
        raise e


if __name__ == "__main__":
    main()
