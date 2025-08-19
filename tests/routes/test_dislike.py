"""
Tests for dislike-related API routes and functionality.

This module tests the dislike routes including dislike creation, retrieval, updates,
and deletion operations.
"""

import pytest
from fastapi.testclient import TestClient

from src.db.models import User, Dislike
from src.routes.dislike import as_dict


@pytest.fixture(name="test_dislike_1")
def test_dislike_1_fixture():
    """Create test dislike data for testing purposes.

    Returns:
        dict: Test dislike data with all required fields
    """
    return {
        "user_id": 1,
        "dislike_name": "test",
        "category": "test",
        "severity": "test",
        "description": "test",
    }


@pytest.fixture(name="test_dislike_2")
def test_dislike_2_fixture():
    """Create second test dislike data for testing purposes.

    Returns:
        dict: Second test dislike data with all required fields
    """
    return {
        "user_id": 1,
        "dislike_name": "test2",
        "category": "test2",
        "severity": "test2",
        "description": "test2",
    }


def test_as_dict(test_dislike_1: Dislike):
    """Test the as_dict utility function for converting Dislike model to dictionary.

    Covers: as_dict() utility function, Dislike model serialization
    """
    unpacked_dict = as_dict(Dislike(**test_dislike_1))
    assert unpacked_dict["user_id"] == test_dislike_1["user_id"]
    assert unpacked_dict["dislike_name"] == test_dislike_1["dislike_name"]
    assert unpacked_dict["category"] == test_dislike_1["category"]
    assert unpacked_dict["description"] == test_dislike_1["description"]


def test_get_dislikes_empty(client: TestClient):
    """Test dislike retrieval for user with no dislikes.

    Covers: GET /dislike/{user_id} route, HTTPException 404 for users with no dislikes
    """
    response = client.get("/dislike/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "No dislikes found for user 1."}


def test_get_dislikes_non_empty(
    client: TestClient,
    test_user: User,
    test_dislike_1: Dislike,
    test_dislike_2: Dislike,
):
    """Test dislike retrieval for user with existing dislikes.

    Covers: GET /dislike/{user_id} route, dislike list retrieval with data
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/dislike", json=test_dislike_1)
    client.post("/dislike", json=test_dislike_2)
    response = client.get("/dislike/1")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_dislike(
    client: TestClient,
    test_user: User,
    test_dislike_1: Dislike,
    test_dislike_2: Dislike,
):
    """Test dislike update with valid data.

    Covers: PUT /dislike/{id} route, successful dislike update
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/dislike", json=test_dislike_1)
    response = client.put("/dislike/1", json=test_dislike_2)
    assert response.status_code == 200
    assert response.json()["dislike_name"] == test_dislike_2["dislike_name"]


def test_delete_dislike(client: TestClient, test_user: User, test_dislike_1: Dislike):
    """Test dislike deletion.

    Covers: DELETE /dislike/{id} route, successful dislike deletion
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/dislike", json=test_dislike_1)
    response = client.delete("/dislike/1")
    assert response.status_code == 200
    assert response.json()["dislike_name"] == test_dislike_1["dislike_name"]
