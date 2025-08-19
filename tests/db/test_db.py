"""Database connection and session management tests.

This module contains tests for the database connection functionality
including session creation, cleanup, and error handling.

Functions
---------
test_get_session_success : None
    Test successful database session creation and retrieval
test_get_session_context_manager : None
    Test proper context manager behavior of get_session function
"""

import pytest
from unittest.mock import MagicMock, patch
from sqlmodel import Session

from src.db import db


def test_get_session_success():
    """Test successful database session creation and retrieval.

    Verifies that the get_session function correctly creates and yields
    a database session from the engine.
    """
    mock_session = MagicMock(spec=Session)

    with patch("src.db.db.Session") as mock_session_class:
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        gen = db.get_session()
        yield_db = next(gen)

        assert mock_session == yield_db


def test_get_session_context_manager():
    """Test proper context manager behavior of get_session function.

    Verifies that the get_session function properly uses the Session
    context manager and yields the session correctly.
    """
    mock_session = MagicMock(spec=Session)

    with patch("src.db.db.Session") as mock_session_class:
        mock_session_class.return_value.__enter__.return_value = mock_session
        mock_session_class.return_value.__exit__.return_value = None

        gen = db.get_session()
        yield_db = next(gen)

        # Verify the session was yielded
        assert mock_session == yield_db

        # Verify the context manager was entered
        mock_session_class.assert_called_once()
        mock_session_class.return_value.__enter__.assert_called_once()

        # Test the generator completion
        with pytest.raises(StopIteration):
            next(gen)

        # Verify the context manager was exited
        mock_session_class.return_value.__exit__.assert_called_once()
