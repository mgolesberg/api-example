"""
Tests for database table initialization functionality.

This module tests the database initialization functions including table creation,
dropping, and test data population.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.db_init import example_data
from src.db_init import tables_initialize


@patch("src.db_init.tables_initialize.SQLModel.metadata.drop_all")
def test_drop_all_tables(mock_drop_all):
    """Test dropping all database tables.

    Covers: drop_all_tables() function, SQLModel metadata drop_all call
    """
    engine = MagicMock()
    tables_initialize.drop_all_tables(engine)
    mock_drop_all.assert_called_once_with(engine)


@patch("src.db_init.tables_initialize.SQLModel.metadata")
def test_create_tables(mock_metadata):
    """Test creating all database tables.

    Covers: create_tables() function, SQLModel metadata create_all call
    """
    engine = MagicMock()
    tables_initialize.create_tables(engine)
    mock_metadata.create_all.assert_called_once_with(engine)


def test_initialize_test_data():
    """Test test data initialization.

    Covers: initialize_test_data() function, session add and commit operations
    """
    session = MagicMock()
    list_of_tables = [
        example_data.TEST_USERS,
        example_data.TEST_ALLERGIES,
        example_data.TEST_INTERESTS,
        example_data.TEST_DISLIKES,
        example_data.TEST_USER_ALLERGIES,
        example_data.TEST_PRODUCTS,
        example_data.TEST_ORDERS,
        example_data.TEST_PURCHASES,
    ]
    number_of_adds = sum(len(table) for table in list_of_tables)
    tables_initialize.initialize_test_data(session)

    assert session.add.call_count == number_of_adds
    assert session.commit.call_count == 2


@patch("src.db_init.tables_initialize.drop_all_tables")
@patch("src.db_init.tables_initialize.create_tables")
@patch("src.db_init.tables_initialize.initialize_test_data")
@patch("src.db_init.tables_initialize.get_session")
def test_main(
    mock_get_session,
    mock_initialize_test_data,
    mock_create_tables,
    mock_drop_all_tables,
):
    """Test main initialization function with successful execution.

    Covers: main() function, successful database initialization flow
    """
    mock_get_session.return_value = MagicMock()

    tables_initialize.main()

    assert mock_get_session.call_count == 1
    assert mock_initialize_test_data.call_count == 1
    assert mock_create_tables.call_count == 1
    assert mock_drop_all_tables.call_count == 1


@patch("src.db_init.tables_initialize.drop_all_tables")
@patch("src.db_init.tables_initialize.create_tables")
@patch("src.db_init.tables_initialize.initialize_test_data")
@patch("src.db_init.tables_initialize.get_session")
def test_main_raises_exception(
    mock_get_session,
    mock_initialize_test_data,
    mock_create_tables,
    mock_drop_all_tables,
):
    """Test main initialization function with exception handling.

    Covers: main() function, exception handling during initialization
    """
    mock_get_session.return_value = MagicMock()
    mock_initialize_test_data.side_effect = Exception("Test exception")

    with pytest.raises(Exception, match="Test exception"):
        tables_initialize.main()

    assert mock_get_session.call_count == 1
    assert mock_initialize_test_data.call_count == 1
    assert mock_create_tables.call_count == 1
    assert mock_drop_all_tables.call_count == 1
