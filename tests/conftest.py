"""
Pytest configuration and fixtures for API testing.

This module provides pytest fixtures and configuration for testing the API application.
It includes database session management, test client setup, and sample data fixtures
for isolated testing of database operations and API endpoints.

Fixtures
--------
session : Session
    In-memory SQLite database session for isolated testing
client : TestClient
    FastAPI test client for making HTTP requests to the API
test_user : User
    Sample user data for testing user-related operations
test_product_1 : Product
    First sample product data for testing product operations
test_product_2 : Product
    Second sample product data for testing product operations
test_interest_1 : Interest
    First sample interest data for testing interest operations
test_interest_2 : Interest
    Second sample interest data for testing interest operations

Notes
-----
- Uses in-memory SQLite database for fast, isolated testing
- Each test gets a fresh database session
- Fixtures provide consistent test data across all test modules
- Database is automatically cleaned up after each test
"""

from datetime import date

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import CheckConstraint
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app import app
from src.db.db import get_session
from src.db.models import User, ConditionEnum


@pytest.fixture(name="session")
def session_fixture():
    """
    Creates a testing database session using an in-memory SQLite database.

    This fixture:
    - Creates an in-memory SQLite engine for fast, isolated testing
    - Creates all database tables using SQLModel.metadata.create_all()
    - Yields a database session that can be used in tests
    - Automatically cleans up the session after each test
    - Completely isolates tests from each other

    Returns:
        Session: A SQLModel database session connected to the test database
    """
    # Remove the specific check from the Table object
    tbl = User.__table__
    for c in list(tbl.constraints):
        if (
            isinstance(c, CheckConstraint)
            and getattr(c, "name", "") == "valid_phone_number"
        ):
            tbl.constraints.remove(c)

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Creates a TestClient with overridden database dependencies for testing.

    This fixture:
    - Overrides the get_session dependency to use the test session instead of production
    - Creates a FastAPI TestClient that can make HTTP requests to your app
    - Automatically cleans up dependency overrides after each test

    The dependency override is crucial because:
    - It prevents tests from using the production database
    - It ensures all API calls in tests use the isolated test database
    - It allows tests to create and manipulate test data safely

    Args:
        session (Session): The test database session from the session_fixture

    Returns:
        TestClient: A configured test client ready for making API requests

    Note:
        This fixture depends on the session fixture and will automatically
        receive the same session instance that the test function gets.
    """

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture():
    """
    Creates a test user instance for testing purposes.

    This fixture provides a valid User model instance with all required
    fields populated with realistic test data. The user is configured
    as ACTIVE and includes all necessary personal and address
    information.

    Returns:
        User: A complete User model instance ready for testing
    """
    return User(
        last_name="TestUser",
        first_name="John",
        birth_date=date(1990, 1, 1),
        email="test.user@example.com",
        phone_number="1234567890",
        condition=ConditionEnum.ACTIVE,
        street1="123 Test Street",
        street2="Apt 1A",
        city="Test City",
        state_province="TS",
        zip="12345",
        country="Test Country",
    )


@pytest.fixture(name="test_product_1")
def test_product_1_fixture():
    """
    Creates test product data for testing purposes.

    Returns:
        dict: Test product data with all required fields
    """
    return {
        "name": "test",
        "description": "test",
        "price": 100,
        "quantity": 10,
        "image_url": "test",
        "category": "test",
        "sub_category": "test",
        "brand": "test",
        "is_active": True,
    }


@pytest.fixture(name="test_product_2")
def test_product_2_fixture():
    """
    Creates second test product data for testing purposes.

    Returns:
        dict: Second test product data with all required fields
    """
    return {
        "name": "test2",
        "description": "test2",
        "price": 200,
        "quantity": 20,
        "image_url": "test2",
        "category": "test2",
        "sub_category": "test2",
        "brand": "test2",
        "is_active": True,
    }


@pytest.fixture(name="test_interest_1")
def test_interest_1_fixture():
    """
    Creates test interest data for testing purposes.

    Returns:
        dict: Test interest data with all required fields
    """
    return {
        "user_id": 1,
        "interest_name": "test",
        "category": "test",
        "description": "test",
    }


@pytest.fixture(name="test_interest_2")
def test_interest_2_fixture():
    """
    Creates second test interest data for testing purposes.

    Returns:
        dict: Second test interest data with all required fields
    """
    return {
        "user_id": 1,
        "interest_name": "test2",
        "category": "test2",
        "description": "test2",
    }
