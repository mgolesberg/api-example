# Test file for base_crud.py routes
"""
This file only has tests for BaseCRUD methods or exceptions
which aren't covered within the routes tests.
"""
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.db.models import Interest
from src.routes.base_crud import BaseCRUD


def test_get_valid(session: Session, client: TestClient, test_interest_1: Interest):
    """Test BaseCRUD.get() method with valid record ID.

    Covers: BaseCRUD.get() method, successful record retrieval
    """
    client.post("/interest", json=test_interest_1)
    crud = BaseCRUD(Interest)
    response = crud.get(session, 1)
    assert response.id == 1
    assert response.interest_name == test_interest_1["interest_name"]


def test_get_missing(session: Session):
    """Test BaseCRUD.get() method with non-existent record ID.

    Covers: BaseCRUD.get() method, HTTPException 404 for missing records
    """
    with pytest.raises(HTTPException) as e:
        crud = BaseCRUD(Interest)
        crud.get(session, 1)
    assert e.value.status_code == 404
    assert e.value.detail == "Record not found"


def test_update_integrity_error(client: TestClient, test_interest_1: Interest):
    """Test BaseCRUD.update() method with database integrity error.

    Covers: BaseCRUD.update() method, HTTPException 422 for integrity errors
    """
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_session.exec.return_value.first.return_value = mock_result
    mock_session.commit.side_effect = IntegrityError(
        "foreign key constraint", "params", "orig"
    )
    client.post("/interest", json=test_interest_1)
    crud = BaseCRUD(Interest)
    with pytest.raises(HTTPException) as e:
        crud.update(mock_session, 1, test_interest_1)
    assert e.value.status_code == 422
    assert "Integrity error" in e.value.detail


def test_delete_missing_record(session: Session):
    """Test BaseCRUD.delete() method with non-existent record ID.

    Covers: BaseCRUD.delete() method, HTTPException 404 for missing records
    """
    crud = BaseCRUD(Interest)
    with pytest.raises(HTTPException) as e:
        crud.delete(session, 1)
    assert e.value.status_code == 404
    assert e.value.detail == "Record not found"


def test_delete_integrity_error(client: TestClient, test_interest_1: Interest):
    """Test BaseCRUD.delete() method with general integrity error.

    Covers: BaseCRUD.delete() method, HTTPException 422 for integrity errors
    """
    mock_session = MagicMock()
    mock_session.delete.side_effect = IntegrityError(
        "Nothing to look at here", "params", "orig"
    )
    client.post("/interest", json=test_interest_1)
    crud = BaseCRUD(Interest)
    with pytest.raises(HTTPException) as e:
        crud.delete(mock_session, 1)
    assert e.value.status_code == 422
    assert "Integrity error" in e.value.detail


def test_delete_foreign_key_error(client: TestClient, test_interest_1: Interest):
    """Test BaseCRUD.delete() method with foreign key constraint error.

    Covers: BaseCRUD.delete() method, HTTPException 409 for foreign key violations
    """
    mock_session = MagicMock()
    mock_session.delete.side_effect = IntegrityError(
        "foreign key constraint", "params", "orig"
    )
    client.post("/interest", json=test_interest_1)
    crud = BaseCRUD(Interest)
    with pytest.raises(HTTPException) as e:
        crud.delete(mock_session, 1)
    assert e.value.status_code == 409
    assert (
        "Cannot delete this record as it is referenced by other records"
        in e.value.detail
    )
