# Test file for interest.py routes
"""
Tests for interest-related API routes and functionality.

TODO: Use this and test_dislike to learn how to parameterize tests
"""

from fastapi.testclient import TestClient

from src.db.models import User, Interest
from src.routes.interest import as_dict


def test_as_dict(test_interest_1: Interest):
    """Test the as_dict utility function for converting Interest model to dictionary.

    Covers: as_dict() utility function, Interest model serialization
    """
    unpacked_dict = as_dict(Interest(**test_interest_1))
    assert unpacked_dict["user_id"] == test_interest_1["user_id"]
    assert unpacked_dict["interest_name"] == test_interest_1["interest_name"]
    assert unpacked_dict["category"] == test_interest_1["category"]
    assert unpacked_dict["description"] == test_interest_1["description"]


def test_get_interests_empty(client: TestClient):
    """Test interest retrieval for user with no interests.

    Covers: GET /interest/{user_id} route, HTTPException 404 for users with no interests
    """
    response = client.get("/interest/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "No interests found for user 1."}


def test_get_interests_non_empty(
    client: TestClient,
    test_user: User,
    test_interest_1: Interest,
    test_interest_2: Interest,
):
    """Test interest retrieval for user with existing interests.

    Covers: GET /interest/{user_id} route, interest list retrieval with data
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/interest", json=test_interest_1)
    client.post("/interest", json=test_interest_2)
    response = client.get("/interest/1")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_interest(
    client: TestClient,
    test_user: User,
    test_interest_1: Interest,
    test_interest_2: Interest,
):
    """Test interest update with valid data.

    Covers: PUT /interest/{id} route, successful interest update
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/interest", json=test_interest_1)
    response = client.put("/interest/1", json=test_interest_2)
    assert response.status_code == 200
    assert response.json()["interest_name"] == test_interest_2["interest_name"]


def test_update_interest_missing(client: TestClient, test_interest_1: Interest):
    """Test interest update for non-existent interest.

    Covers: PUT /interest/{id} route, HTTPException 404 for missing interests
    """
    response = client.put("/interest/1", json=test_interest_1)
    assert response.status_code == 404
    assert response.json() == {"detail": "Record not found"}


def test_delete_interest(
    client: TestClient, test_user: User, test_interest_1: Interest
):
    """Test interest deletion.

    Covers: DELETE /interest/{id} route, successful interest deletion
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/interest", json=test_interest_1)
    response = client.delete("/interest/1")
    assert response.status_code == 200
    assert response.json()["interest_name"] == test_interest_1["interest_name"]
