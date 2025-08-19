# Test file for order_and_purchase.py routes
"""
Tests for order and purchase-related API routes and functionality.

This module tests the order and purchase routes including order creation, purchase
management, quantity updates, and checkout operations.

Note: I am not sure how to trigger the final try/except block in update_purchase_quantity
given that orders is required earlier in the code
"""

from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.exc import DataError, IntegrityError
from sqlmodel import Session, select

from src.db.models import Order, Product, PurchaseBase, User
from src.routes.order_and_purchase import buy_CRUD


@pytest.fixture()
def generate_product_1(session: Session, test_product_1: dict):
    """Create and return a test product with UUID for testing.

    Args:
        session (Session): Database session
        test_product_1 (dict): Test product data

    Returns:
        UUID: Generated product UUID
    """
    uuid = uuid4()
    product = Product(id=uuid, **test_product_1)
    session.add(product)
    session.commit()
    return uuid


@pytest.fixture()
def generate_product_2(session: Session, test_product_1: dict):
    """Create and return a second test product with UUID for testing.

    Args:
        session (Session): Database session
        test_product_1 (dict): Test product data

    Returns:
        UUID: Generated product UUID
    """
    uuid = uuid4()
    product = Product(id=uuid, **test_product_1)
    session.add(product)
    session.commit()
    return uuid


def test_create_order(
    client: TestClient, session: Session, test_user: User, test_product_1: dict
):
    """Test order creation with valid product and user.

    Covers: POST /buy route, successful order creation with purchase
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/product", json=test_product_1)
    product = session.exec(
        select(Product).where(Product.name == test_product_1["name"])
    ).first()
    response = client.post(
        "/buy", json={"user_id": 1, "product_id": str(product.id), "quantity": 1}
    )
    assert response.status_code == 200
    assert response.json()["order"]["id"] == 1
    assert response.json()["order"]["user_id"] == 1
    assert response.json()["order"]["checked_out"] is False
    assert len(response.json()["purchases"]) == 1
    assert response.json()["purchases"][0]["product_id"] == str(product.id)


def test_get_order_with_two_products(
    client: TestClient,
    session: Session,
    test_user: User,
    test_product_1: dict,
    test_product_2: dict,
):
    """Test order retrieval with multiple products.

    Covers: GET /buy/{user_id} route, order retrieval with multiple purchases
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/product", json=test_product_1)
    client.post("/product", json=test_product_2)
    product_1 = session.exec(
        select(Product).where(Product.name == test_product_1["name"])
    ).first()
    product_2 = session.exec(
        select(Product).where(Product.name == test_product_2["name"])
    ).first()
    client.post(
        "/buy", json={"user_id": 1, "product_id": str(product_1.id), "quantity": 1}
    )
    client.post(
        "/buy", json={"user_id": 1, "product_id": str(product_2.id), "quantity": 1}
    )
    response = client.get("/buy/1")
    assert response.status_code == 200
    assert response.json()[0]["order"]["id"] == 1
    assert response.json()[0]["order"]["user_id"] == 1
    assert len(response.json()[0]["purchases"]) == 2
    assert response.json()[0]["purchases"][0]["product_id"] == str(product_1.id)


def test_create_order_with_missing_product(client: TestClient):
    """Test order creation with non-existent product.

    Covers: POST /buy route, HTTPException 404 for missing products
    """
    response = client.post(
        "/buy", json={"user_id": 1, "product_id": str(uuid4()), "quantity": 1}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_create_product_when_it_is_already_in_order(
    client: TestClient, session: Session, test_user: User, test_product_1: dict
):
    """Test adding product to order when it already exists.

    Covers: POST /buy route, quantity aggregation for existing products in order
    """
    first_quantity = 1
    second_quantity = 2
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/product", json=test_product_1)
    product_1 = session.exec(
        select(Product).where(Product.name == test_product_1["name"])
    ).first()
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1.id),
            "quantity": first_quantity,
        },
    )
    response = client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1.id),
            "quantity": second_quantity,
        },
    )
    assert response.status_code == 200
    assert len(response.json()["purchases"]) == 1
    assert (
        response.json()["purchases"][0]["quantity"] == first_quantity + second_quantity
    )


def test_create_product_with_open_order(
    client: TestClient, session: Session, test_user: User, test_product_1: dict
):
    """Test adding product to existing open order.

    Covers: POST /buy route, adding products to existing open orders
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/product", json=test_product_1)
    product_1 = session.exec(
        select(Product).where(Product.name == test_product_1["name"])
    ).first()
    session.add(Order(user_id=1, total_amount=3.50))
    session.commit()
    response = client.post(
        "/buy", json={"user_id": 1, "product_id": str(product_1.id), "quantity": 1}
    )
    assert response.status_code == 200
    assert response.json()["order"]["id"] == 1


def test_create_product_too_many_open_orders_error(
    client: TestClient, session: Session, test_user: User, test_product_1: dict
):
    """Test order creation with multiple open orders.

    Covers: POST /buy route, HTTPException 409 for multiple open orders
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    client.post("/product", json=test_product_1)
    product_1 = session.exec(
        select(Product).where(Product.name == test_product_1["name"])
    ).first()
    session.add(Order(user_id=1, total_amount=3.50))
    session.add(Order(user_id=1, total_amount=4.20))
    session.commit()
    response = client.post(
        "/buy", json={"user_id": 1, "product_id": str(product_1.id), "quantity": 1}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Multiple open orders found for user 1"


def test_crud_create_integrity_error(
    client: TestClient, session: Session, test_product_1: Product
):
    """Test purchase creation with database integrity error.

    Covers: buy_CRUD.create_purchase() method, HTTPException 422 for integrity errors
    """
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    base_purchase = PurchaseBase(user_id=1, product_id=product_1_id, quantity=1)
    with patch(
        "src.routes.order_and_purchase.Purchase",
        side_effect=IntegrityError("statement", "params", "orig"),
    ):
        # Don't patch Purchase until after we have one in the database
        with pytest.raises(HTTPException) as e:
            buy_CRUD.create_purchase(session, base_purchase)
    assert e.value.status_code == 422
    assert "Integrity error" in e.value.detail


def test_crud_create_data_error(
    client: TestClient, session: Session, test_product_1: Product
):
    """Test purchase creation with database data error.

    Covers: buy_CRUD.create_purchase() method, HTTPException 422 for data errors
    """
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    base_purchase = PurchaseBase(user_id=1, product_id=product_1_id, quantity=1)
    with patch(
        "src.routes.order_and_purchase.Purchase",
        side_effect=DataError("statement", "params", "orig"),
    ):
        # Don't patch Purchase until after we have one in the database
        with pytest.raises(HTTPException) as e:
            buy_CRUD.create_purchase(session, base_purchase)
    assert e.value.status_code == 422
    assert "Data error" in e.value.detail


def test_update_purchase_quantity(
    client: TestClient, test_user: User, test_product_1: dict
):
    """Test purchase quantity update with valid data.

    Covers: PUT /buy route, successful purchase quantity update
    """
    first_quantity = 1
    second_quantity = 2
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1_id),
            "quantity": first_quantity,
        },
    )
    base_purchase = PurchaseBase(
        user_id=1, product_id=product_1_id, quantity=second_quantity
    )
    response = client.put("/buy", json=base_purchase.model_dump(mode="json"))
    assert response.status_code == 200
    assert len(response.json()["purchases"]) == 1
    assert (
        response.json()["purchases"][0]["quantity"] == first_quantity + second_quantity
    )


def test_update_purchase_quantity_too_many_open_orders_error(
    client: TestClient, session: Session, test_user: User, test_product_1: dict
):
    """Test purchase quantity update with multiple open orders.

    Covers: PUT /buy route, HTTPException 409 for multiple open orders
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    session.add(Order(user_id=1, total_amount=3.50))
    session.add(Order(user_id=1, total_amount=4.20))
    session.commit()
    response = client.put(
        "/buy", json={"user_id": 1, "product_id": product_1_id, "quantity": 1}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Multiple open orders found for user 1"


def test_update_purchase_quantity_order_not_found_error(
    client: TestClient, test_user: User, test_product_1: dict
):
    """Test purchase quantity update for user with no open order.

    Covers: PUT /buy route, HTTPException 404 for missing orders
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    base_purchase = PurchaseBase(user_id=1, product_id=product_1_id, quantity=1)
    response = client.put("/buy", json=base_purchase.model_dump(mode="json"))
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]


def test_update_purchase_quantity_product_not_found_error(
    client: TestClient, test_user: User, test_product_1: dict
):
    """Test purchase quantity update for product not in user's cart.

    Covers: PUT /buy route, HTTPException 404 for products not in cart
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1_id),
            "quantity": 1,
        },
    )
    different_product_id = uuid4()
    base_purchase = PurchaseBase(user_id=1, product_id=different_product_id, quantity=1)
    response = client.put("/buy", json=base_purchase.model_dump(mode="json"))
    assert response.status_code == 404
    assert "Product" in response.json()["detail"]
    assert "not found in cart for user 1" in response.json()["detail"]


def test_update_purchase_negative_quantity(
    client: TestClient, test_user: User, test_product_1: dict
):
    """Test purchase quantity update with negative quantity.

    Covers: PUT /buy route, purchase removal when quantity becomes negative
    """
    first_quantity = 2
    second_quantity = -3
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1_id),
            "quantity": first_quantity,
        },
    )
    base_purchase = PurchaseBase(
        user_id=1, product_id=product_1_id, quantity=second_quantity
    )
    response = client.put("/buy", json=base_purchase.model_dump(mode="json"))
    assert response.status_code == 200
    assert len(response.json()["purchases"]) == 0
    assert response.json()["order"]["total_amount"] == "0.00"


def test_update_purchase_zero_quantity(
    client: TestClient, test_user: User, test_product_1: dict
):
    """Test purchase quantity update with zero quantity.

    Covers: PUT /buy route, HTTPException 400 for zero quantity changes
    """
    first_quantity = 2
    second_quantity = 0
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1_id),
            "quantity": first_quantity,
        },
    )
    base_purchase = PurchaseBase(
        user_id=1, product_id=product_1_id, quantity=second_quantity
    )
    response = client.put("/buy", json=base_purchase.model_dump(mode="json"))
    assert response.status_code == 400
    assert response.json()["detail"] == "Quantity change cannot be 0"


@pytest.mark.skip(
    reason="Not sure mock all my logic to get to the final try/except block"
)
@patch("src.routes.order_and_purchase.buyCRUD.update_purchase_quantity")
def test_update_purchase_quantity_integrity_error(mock_method, session: Session):
    """Test purchase quantity update with database integrity error.

    Covers: PUT /buy route, HTTPException 422 for integrity errors during update

    Note: This test is skipped as the mocking logic is complex
    """
    mock_method.statement = MagicMock()
    mock_method.product = MagicMock()
    uuid = uuid4()
    mock_purchase = {
        "id": uuid,
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
    mock_method.orders = [[{"order": MagicMock(), "purchases": [mock_purchase]}]]
    mock_method.orders_count = 1
    mock_method.orders[0][0].order.updated_at.side_effect = IntegrityError(
        "statement", "params", "orig"
    )
    base_purchase = PurchaseBase(user_id=1, product_id=uuid, quantity=1)
    with pytest.raises(HTTPException) as e:
        buy_CRUD.create_purchase(session, base_purchase)
    assert e.value.status_code == 422
    assert "Integrity error" in e.value.detail


def test_delete_purchase(client: TestClient, test_user: User, test_product_1: dict):
    """Test purchase deletion.

    Covers: DELETE /buy route, successful purchase deletion
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1_id),
            "quantity": 1,
        },
    )
    response = client.delete("/buy?user_id=1&product_id=" + str(product_1_id))
    assert response.status_code == 200
    assert len(response.json()["purchases"]) == 0
    assert response.json()["order"]["total_amount"] == "0.00"


def test_delete_purchase_not_found(client: TestClient):
    """Test purchase deletion for non-existent purchase.

    Covers: DELETE /buy route, HTTPException 404 for missing purchases
    """
    response = client.delete("/buy?user_id=1&product_id=" + str(uuid4()))
    assert response.status_code == 404
    assert "Product" in response.json()["detail"]
    assert "not found in cart for user 1" in response.json()["detail"]


def test_checkout_no_open_order(client: TestClient):
    """Test checkout for user with no open order.

    Covers: POST /buy/checkout/{user_id} route, HTTPException 404 for no open orders
    """
    response = client.post("/buy/checkout/1")
    assert response.status_code == 404
    assert response.json()["detail"] == "No open order found for user 1"


def test_checkout_not_enough_inventory(
    client: TestClient, test_user: User, test_product_1: dict
):
    """Test checkout with insufficient inventory.

    Covers: POST /buy/checkout/{user_id} route, HTTPException 400 for insufficient inventory
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy",
        json={
            "user_id": 1,
            "product_id": str(product_1_id),
            "quantity": test_product_1["quantity"] + 1,
        },
    )
    response = client.post("/buy/checkout/1")
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough test in inventory"


def test_checkout_success(
    client: TestClient, session: Session, test_user: User, test_product_1: dict
):
    """Test successful checkout process.

    Covers: POST /buy/checkout/{user_id} route, successful checkout with inventory update
    """
    client.post("/user", json=test_user.model_dump(mode="json"))
    product_1 = client.post("/product", json=test_product_1)
    product_1_id = product_1.json()["id"]
    client.post(
        "/buy", json={"user_id": 1, "product_id": str(product_1_id), "quantity": 3}
    )
    response = client.post("/buy/checkout/1")
    assert response.status_code == 200
    assert response.json()["order"]["checked_out"] is True
    assert response.json()["purchases"][0]["status"] == "Purchased"
    assert response.json()["purchases"][0]["quantity"] == 3
    product_1 = session.exec(
        select(Product).where(Product.name == test_product_1["name"])
    ).first()
    assert product_1.quantity == test_product_1["quantity"] - 3
