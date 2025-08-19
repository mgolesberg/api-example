"""
Tests for allergy-related API routes and functionality.

This module tests the allergy routes including allergy creation, retrieval, updates,
and deletion operations.
"""

from fastapi.testclient import TestClient


def test_get_allergies_empty(client: TestClient):
    """Test allergy list retrieval when no allergies exist.

    Covers: GET /allergy route, empty allergy list response
    """
    response = client.get("/allergy")
    assert response.status_code == 200
    assert response.json() == []


def test_get_allergies_non_empty(client: TestClient):
    """Test allergy list retrieval with existing allergies.

    Covers: GET /allergy route, allergy list retrieval with data
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    client.post("/allergy", json={"name": "test2", "description": "test2"})
    response = client.get("/allergy")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "test"


def test_create_allergy_valid(client: TestClient):
    """Test allergy creation with valid data.

    Covers: POST /allergy route, successful allergy creation
    """
    response = client.post("/allergy", json={"name": "test", "description": "test"})
    assert response.status_code == 200
    assert response.json()["name"] == "test"


def test_create_allergy_invalid(client: TestClient):
    """Test allergy creation with duplicate name.

    Covers: POST /allergy route, HTTPException 422 for duplicate allergy names
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    response = client.post("/allergy", json={"name": "test", "description": "test"})
    assert response.status_code == 422
    assert "Integrity error" in response.json()["detail"]


def test_update_allergy_valid(client: TestClient):
    """Test allergy update with valid data.

    Covers: PUT /allergy/{name} route, successful allergy update
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    response = client.put("/allergy/test", json={"description": "test2"})
    assert response.status_code == 200
    assert response.json()["description"] == "test2"


def test_update_allergy_invalid(client: TestClient):
    """Test allergy update with duplicate name.

    Covers: PUT /allergy/{name} route, HTTPException 422 for duplicate allergy names
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    client.post("/allergy", json={"name": "test2", "description": "test"})
    response = client.put("/allergy/test2", json={"name": "test"})
    assert response.status_code == 422
    assert "Integrity error" in response.json()["detail"]


def test_update_allergy_not_found(client: TestClient):
    """Test allergy update for non-existent allergy.

    Covers: PUT /allergy/{name} route, HTTPException 404 for missing allergies
    """
    response = client.put("/allergy/test", json={"description": "test2"})
    assert response.status_code == 404


def test_delete_allergy_valid(client: TestClient):
    """Test allergy deletion.

    Covers: DELETE /allergy/{name} route, successful allergy deletion
    """
    client.post("/allergy", json={"name": "test", "description": "test"})
    response = client.delete("/allergy/test")
    assert response.status_code == 200


def test_delete_allergy_not_found(client: TestClient):
    """Test allergy deletion for non-existent allergy.

    Covers: DELETE /allergy/{name} route, HTTPException 404 for missing allergies
    """
    response = client.delete("/allergy/test")
    assert response.status_code == 404
