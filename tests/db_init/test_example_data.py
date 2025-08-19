"""
Tests for example data functionality.

This module tests the example data loading and generation functions used
for testing and development purposes.
"""

from sqlmodel import Session, func

from src.db import models
from src.db_init import example_data


def test_example_data():
    """Test that the example data is loaded correctly.

    Covers: example_data module data loading, all test data constants
    """
    assert example_data.TEST_USERS is not None
    assert example_data.TEST_INTERESTS is not None
    assert example_data.TEST_DISLIKES is not None
    assert example_data.TEST_ALLERGIES is not None
    assert example_data.TEST_USER_ALLERGIES is not None
    assert example_data.TEST_PRODUCTS is not None
    assert example_data.TEST_ORDERS is not None
    assert example_data.TEST_PURCHASES is not None


def test_generate_test_data(session: Session):
    """Test generating test data in the database.

    Covers: example_data constants, database model creation, data validation
    """
    for user in example_data.TEST_USERS:
        session.add(models.User(**user))
    for interest in example_data.TEST_INTERESTS:
        session.add(models.Interest(**interest))
    for dislike in example_data.TEST_DISLIKES:
        session.add(models.Dislike(**dislike))
    for allergy in example_data.TEST_ALLERGIES:
        session.add(models.Allergy(**allergy))
    for user_allergy in example_data.TEST_USER_ALLERGIES:
        session.add(models.UserAllergy(**user_allergy))
    for product in example_data.TEST_PRODUCTS:
        session.add(models.Product(**product))
    for order in example_data.TEST_ORDERS:
        session.add(models.Order(**order))
    for purchase in example_data.TEST_PURCHASES:
        session.add(models.Purchase(**purchase))
    session.commit()
    assert session.exec(func.count(models.User.id)).one()[0] == len(
        example_data.TEST_USERS
    )
    assert session.exec(func.count(models.Interest.id)).one()[0] == len(
        example_data.TEST_INTERESTS
    )
    assert session.exec(func.count(models.Dislike.id)).one()[0] == len(
        example_data.TEST_DISLIKES
    )
    assert session.exec(func.count(models.Allergy.name)).one()[0] == len(
        example_data.TEST_ALLERGIES
    )
    assert session.exec(func.count(models.UserAllergy.user_id)).one()[0] == len(
        example_data.TEST_USER_ALLERGIES
    )
    assert session.exec(func.count(models.Product.id)).one()[0] == len(
        example_data.TEST_PRODUCTS
    )
    assert session.exec(func.count(models.Order.id)).one()[0] == len(
        example_data.TEST_ORDERS
    )
    assert session.exec(func.count(models.Purchase.id)).one()[0] == len(
        example_data.TEST_PURCHASES
    )
