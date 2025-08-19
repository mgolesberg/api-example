# Test file for user.py routes
"""
Tests for user-related API routes and functionality.

This module tests the user routes including user creation, retrieval, updates,
deactivation, deletion marking, and allergy management operations.
"""

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.db.models import User
from src.routes.user import CRUD, as_dict


def test_as_dict(test_user: User):
    """Test the as_dict utility function for converting User model to dictionary.

    Covers: as_dict() utility function, User model serialization
    """
    unpacked_dict = as_dict(test_user)
    assert unpacked_dict["last_name"] == test_user.last_name
    assert unpacked_dict["first_name"] == test_user.first_name
    assert unpacked_dict["street1"] == test_user.street1


def test_validate_phone_number_error():
    """Test phone number validation with invalid format.

    Covers: CRUD._validate_phone_number() method, HTTPException for invalid phone numbers
    """
    crud = CRUD(User)
    with pytest.raises(HTTPException) as e:
        crud._validate_phone_number("1xasfd")
        assert "Phone number must be in the format +1234567890" in e.value.detail


def test_create_user_valid(client: TestClient, test_user: User):
    """Test user creation with valid data.

    Covers: POST /user route, successful user creation
    """
    response = client.post("/user", json=test_user.model_dump(mode="json"))
    assert response.status_code == 200

    expected_data = test_user.model_dump(mode="json")
    expected_data["id"] = 1
    assert response.json() == expected_data


def test_create_user_who_is_inactive(client: TestClient, test_user: User):
    """Test user creation when user was previously deactivated.

    Covers: POST /user route, user reactivation logic
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.put("/user/1/deactivate")
    test_user.id = 1
    del test_user.birth_date  # SQLite doesn't like dates the same way postgres does
    response = client.post("/user", json=test_user.model_dump(mode="json"))
    assert response.status_code == 200
    assert response.json()["condition"] == "Active"


def test_create_user_duplicate(client: TestClient, test_user: User):
    """Test user creation with duplicate email.

    Covers: POST /user route, duplicate email handling, HTTPException 422
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.post("/user", json=test_user.model_dump(mode="json"))
    assert response.status_code == 422
    assert "User with email" in response.json()["detail"]


def test_create_user_integrity_error(client: TestClient):
    """Test user creation with invalid data causing integrity error.

    Covers: POST /user route, data validation, HTTPException 422 for integrity errors
    """
    response = client.post("/user", json={"city": 17, "birth_date": "1990-01-01"})
    assert response.status_code == 422
    assert "Integrity error" in response.json()["detail"]


def test_get_user_empty(client: TestClient):
    """Test user retrieval when no users exist.

    Covers: GET /user/{id} route, HTTPException 404 for non-existent users
    """
    response = client.get("/user/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "No user found with email or id 1"}


def test_get_user_valid_int(client: TestClient, test_user: User):
    """Test user retrieval by integer ID.

    Covers: GET /user/{id} route, successful user retrieval by ID
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.get("/user/1")
    assert response.status_code == 200
    assert response.json()["zip"] == test_user.zip


def test_get_user_valid_email(client: TestClient, test_user: User):
    """Test user retrieval by email address.

    Covers: GET /user/{email} route, successful user retrieval by email
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.get(f"/user/{test_user.email}")
    assert response.status_code == 200
    assert response.json()["zip"] == test_user.zip


def test_update_user_int(client: TestClient, test_user: User):
    """Test user profile update by integer ID.

    Covers: PUT /user/{id}/profile route, successful profile update by ID
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.put("/user/1/profile", json={"city": "New York City"})
    assert response.status_code == 200
    assert response.json()["city"] == "New York City"


def test_update_user_email(client: TestClient, test_user: User):
    """Test user profile update by email address.

    Covers: PUT /user/{email}/profile route, successful profile update by email
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.put(
        f"/user/{test_user.email}/profile", json={"city": "New York City"}
    )
    assert response.status_code == 200
    assert response.json()["city"] == "New York City"


def test_update_user_missing(client: TestClient):
    """Test user profile update for non-existent user.

    Covers: PUT /user/{id}/profile route, HTTPException 404 for missing users
    """
    response = client.put("/user/1/profile", json={"city": "New York City"})
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found with email or id 1"}


def test_update_user_integrity_error(client: TestClient, test_user: User):
    """Test user profile update causing integrity error.

    Covers: PUT /user/{id}/profile route, HTTPException 422 for integrity errors
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    test_user.email = "different@email"
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.put("/user/1/profile", json={"email": "different@email"})
    assert response.status_code == 422
    assert "Integrity error" in response.json()["detail"]


def test_deactivate_user(client: TestClient, test_user: User):
    """Test user deactivation.

    Covers: PUT /user/{id}/deactivate route, user status change to Deactivated
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.put("/user/1/deactivate")
    assert response.status_code == 200
    assert response.json()["condition"] == "Deactivated"


def test_mark_for_deletion(client: TestClient, test_user: User):
    """Test marking user for deletion.

    Covers: PUT /user/{id}/delete route, user status change to Marked for deletion
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.put("/user/1/delete")
    assert response.status_code == 200
    assert response.json()["condition"] == "Marked for deletion"


def test_get_allergies_empty_int(client: TestClient, test_user: User):
    """Test retrieving allergies for user with no allergies by integer ID.

    Covers: GET /user/{id}/allergies route, empty allergy list response
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.get("/user/1/allergies")
    assert response.status_code == 200
    assert response.json() == []


def test_get_allergies_empty_email(client: TestClient, test_user: User):
    """Test retrieving allergies for user with no allergies by email.

    Covers: GET /user/{email}/allergies route, empty allergy list response
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.get(f"/user/{test_user.email}/allergies")
    assert response.status_code == 200
    assert response.json() == []


def test_get_allergies_invalid_int(client: TestClient):
    """Test retrieving allergies for non-existent user.

    Covers: GET /user/{id}/allergies route, HTTPException 404 for missing users
    """
    response = client.get("/user/1/allergies")
    assert response.status_code == 404
    assert response.json() == {"detail": "No user found with email or id 1"}


def test_get_allergies_with_data(client: TestClient, test_user: User):
    """Test retrieving allergies for user with assigned allergies.

    Covers: GET /user/{id}/allergies route, allergy list retrieval with data
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/allergy", json={"name": "test", "description": "test"})
    client.post("/user/1/allergies?allergy_name=test")
    response = client.get("/user/1/allergies")
    assert response.status_code == 200
    assert response.json() == [{"name": "test", "description": "test"}]


def test_add_allergy_no_allergy(client: TestClient, test_user: User):
    """Test adding non-existent allergy to user.

    Covers: POST /user/{id}/allergies route, HTTPException 404 for missing allergies
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.post("/user/1/allergies?allergy_name=test")
    assert response.status_code == 404
    assert response.json() == {"detail": "Allergy test not found"}


def test_add_allergy_no_user(client: TestClient):
    """Test adding allergy to non-existent user.

    Covers: POST /user/{id}/allergies route, HTTPException 404 for missing users
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    response = client.post("/user/1/allergies?allergy_name=test")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 1 not found"}


def test_add_allergy_duplicate(client: TestClient, test_user: User):
    """Test adding duplicate allergy to user.

    Covers: POST /user/{id}/allergies route, HTTPException 409 for duplicate allergies
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/allergy", json={"name": "test", "description": "test"})
    client.post("/user/1/allergies?allergy_name=test")
    response = client.post("/user/1/allergies?allergy_name=test")
    assert response.status_code == 409
    assert response.json() == {"detail": "Allergy test already exists for user"}


def test_delete_allergy(client: TestClient, test_user: User):
    """Test removing allergy from user.

    Covers: DELETE /user/{id}/allergies route, successful allergy removal
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/allergy", json={"name": "test", "description": "test"})
    client.post("/allergy", json={"name": "test2", "description": "test2"})
    client.post("/user/1/allergies?allergy_name=test")
    client.post("/user/1/allergies?allergy_name=test2")
    response = client.delete("/user/1/allergies?allergy_name=test")
    assert response.status_code == 200
    assert response.json() == [{"name": "test2", "description": "test2"}]


def test_delete_allergy_no_allergy(client: TestClient, test_user: User):
    """Test removing non-existent allergy from user.

    Covers: DELETE /user/{id}/allergies route, HTTPException 404 for missing allergies
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    response = client.delete("/user/1/allergies?allergy_name=test")
    assert response.status_code == 404
    assert response.json() == {"detail": "Allergy test not found"}


def test_delete_allergy_no_user(client: TestClient):
    """Test removing allergy from non-existent user.

    Covers: DELETE /user/{id}/allergies route, HTTPException 404 for missing users
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    response = client.delete("/user/1/allergies?allergy_name=test")
    assert response.status_code == 404
    assert response.json() == {"detail": "User with id 1 not found"}


def test_delete_allergy_not_assigned_to_user(client: TestClient, test_user: User):
    """Test removing allergy that is not assigned to user.

    Covers: DELETE /user/{id}/allergies route, HTTPException 404 for unassigned allergies
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/allergy", json={"name": "test", "description": "test"})
    response = client.delete("/user/1/allergies?allergy_name=test")
    assert response.status_code == 404
    assert response.json() == {"detail": "Allergy test not found for user"}
