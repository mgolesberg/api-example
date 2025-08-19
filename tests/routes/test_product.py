# Test file for product.py routes
"""
Tests for product-related API routes and functionality.

SQLite memory doesn't work well with UUIDs the way it does in postgres,
so I skipped all the tests that involve UUIDs for now.
"""

from unittest.mock import patch
from uuid import UUID, uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from src.db.models import Product
from src.routes.product import as_dict, product_CRUD


def test_as_dict(test_product_1: Product):
    """Test the as_dict utility function for converting Product model to dictionary.

    Covers: as_dict() utility function, Product model serialization
    """
    unpacked_dict = as_dict(Product(**test_product_1))
    assert unpacked_dict["name"] == test_product_1["name"]
    assert unpacked_dict["description"] == test_product_1["description"]
    assert unpacked_dict["price"] == test_product_1["price"]
    assert unpacked_dict["quantity"] == test_product_1["quantity"]


def test_get_products_empty(client: TestClient):
    """Test product list retrieval when no products exist.

    Covers: GET /product/ route, empty product list response
    """
    response = client.get("/product/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_products_non_empty(
    client: TestClient, test_product_1: Product, test_product_2: Product
):
    """Test product list retrieval with existing products.

    Covers: GET /product/ route, product list retrieval with data
    """
    client.post("/product", json=test_product_1)
    client.post("/product", json=test_product_2)
    response = client.get("/product/")
    assert response.status_code == 200
    assert len(response.json()) == 2


@patch("src.routes.product.product_CRUD.get")
def test_get_product_valid(mock_get, client: TestClient, test_product_1: Product):
    """Test product retrieval by ID with mocked CRUD.

    Covers: GET /product/{id} route, successful product retrieval
    """
    mock_get.return_value = test_product_1
    response = client.get("/product/1")
    assert response.status_code == 200


@patch("src.routes.product.product_CRUD.create")
def test_create_product(mock_create, client: TestClient, test_product_1: Product):
    """Test product creation with mocked CRUD.

    Covers: POST /product route, successful product creation
    """
    mock_create.return_value = test_product_1
    response = client.post("/product", json=test_product_1)
    assert response.status_code == 200


@patch("src.routes.product.product_CRUD.update")
def test_update_product(mock_update, client: TestClient, test_product_1: Product):
    """Test product update with mocked CRUD.

    Covers: PUT /product/{id} route, successful product update
    """
    mock_update.return_value = test_product_1
    response = client.put("/product/1", json=test_product_1)
    assert response.status_code == 200


@patch("src.routes.product.product_CRUD.delete")
def test_delete_product(mock_delete, client: TestClient, test_product_1: Product):
    """Test product deletion with mocked CRUD.

    Covers: DELETE /product/{id} route, successful product deletion
    """
    mock_delete.return_value = test_product_1
    response = client.delete("/product/1")
    assert response.status_code == 200


def test_crud_update_missing(session: Session, test_product_1: Product):
    """Test product CRUD update with non-existent product ID.

    Covers: product_CRUD.update() method, HTTPException 404 for missing products
    """
    uuid = uuid4()
    with pytest.raises(HTTPException) as e:
        product_CRUD.update(session, str(uuid), test_product_1)
    assert e.value.status_code == 404
    assert e.value.detail == "Record not found"


def test_crud_update_valid(
    session: Session,
    client: TestClient,
    test_product_1: Product,
    test_product_2: Product,
):
    """Test product CRUD update with valid product ID.

    Covers: product_CRUD.update() method, successful product update
    """
    response = client.post("/product", json=test_product_1)
    uuid = response.json()["id"]
    result = product_CRUD.update(session, uuid, test_product_2)
    assert result.id == UUID(uuid)
    assert result.name == test_product_2["name"]


@patch(
    "src.routes.product.select",
    side_effect=IntegrityError("statement", "params", "orig"),
)
def test_crud_update_integrity_error(session: Session, test_product_1: Product):
    """Test product CRUD update with database integrity error.

    Covers: product_CRUD.update() method, HTTPException 422 for integrity errors
    """
    uuid = uuid4()
    with pytest.raises(HTTPException) as e:
        product_CRUD.update(session, str(uuid), test_product_1)
    assert e.value.status_code == 422
    assert "Integrity error" in e.value.detail
