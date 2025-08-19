"""Database models testing module.

This module contains tests for the models in the db package.
It uses the session fixture from conftest for isolated testing.

Classes
-------
TestUsers : class
    Test cases for User model operations
TestInterest : class
    Test cases for Interest model operations
TestDislike : class
    Test cases for Dislike model operations
TestAllergy : class
    Test cases for Allergy model operations
TestProduct : class
    Test cases for Product model operations
TestOrder : class
    Test cases for Order model operations
TestPurchase : class
    Test cases for Purchase model operations

Notes
-----
This module uses the session fixture from conftest which provides
an isolated in-memory SQLite database for testing.
"""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session
from src.db import models


class TestUsers:
    """Test class for User model operations.

    Tests user creation, validation, and constraint enforcement.
    """

    def test_create_valid_user(self, session: Session):
        """Test creating a valid user with all required fields.

        Verifies that a user can be created with all required fields
        and that the ID is properly assigned.
        """
        user = models.User(
            last_name="Doe",
            first_name="John",
            birth_date=date(1990, 1, 1),
            email="john.doe@example.com",
            phone_number="+1234567890",
            condition=models.ConditionEnum.ACTIVE,
            street1="123 Main St",
            street2="Apt 4B",
            city="Anytown",
            state_province="CA",
            zip="12345",
            country="USA",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.last_name == "Doe"
        assert user.first_name == "John"
        assert user.email == "john.doe@example.com"
        assert user.phone_number == "+1234567890"
        assert user.condition == models.ConditionEnum.ACTIVE
        assert user.street1 == "123 Main St"
        assert user.street2 == "Apt 4B"
        assert user.city == "Anytown"
        assert user.state_province == "CA"
        assert user.zip == "12345"
        assert user.country == "USA"

    def test_create_user_without_optional_fields(self, session: Session):
        """Test creating a user without optional fields.

        Verifies that a user can be created without optional fields
        and that None values are properly handled.
        """
        user = models.User(
            last_name="Smith",
            first_name="Jane",
            birth_date=date(1985, 5, 15),
            email="jane.smith@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="456 Oak Ave",
            city="Somewhere",
            state_province="NY",
            zip="54321",
            country="USA",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.phone_number is None
        assert user.street2 is None

    def test_create_user_with_different_conditions(self, session: Session):
        """Test creating users with different condition values.

        Verifies that all condition enum values can be used
        when creating users.
        """
        conditions = [
            models.ConditionEnum.ACTIVE,
            models.ConditionEnum.DEACTIVATED,
            models.ConditionEnum.MARKED_FOR_DELETION,
            models.ConditionEnum.TEST,
            models.ConditionEnum.NO_LONGER_IN_STOCK,
        ]

        for i, condition in enumerate(conditions):
            user = models.User(
                last_name=f"User{i}",
                first_name=f"Test{i}",
                birth_date=date(1990, 1, 1),
                email=f"user{i}@example.com",
                condition=condition,
                street1="123 Test St",
                city="Test City",
                state_province="TX",
                zip="12345",
                country="USA",
            )

            session.add(user)
            session.commit()
            session.refresh(user)

            assert user.condition == condition

    def test_create_user_with_duplicate_email(self, session: Session):
        """Test creating a user with duplicate email (should fail).

        Verifies that the unique constraint on email addresses
        is properly enforced.
        """
        user1 = models.User(
            last_name="First",
            first_name="User",
            birth_date=date(1990, 1, 1),
            email="duplicate@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="123 Test St",
            city="Test City",
            state_province="TX",
            zip="12345",
            country="USA",
        )

        user2 = models.User(
            last_name="Second",
            first_name="User",
            birth_date=date(1991, 2, 2),
            email="duplicate@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="456 Test St",
            city="Test City",
            state_province="TX",
            zip="12345",
            country="USA",
        )

        session.add(user1)
        session.commit()
        session.add(user2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_create_user_missing_required_fields(self, session: Session):
        """Test creating a user with missing required fields.

        Verifies that required field constraints are enforced
        and users cannot be created without essential information.
        """
        user = models.User(
            last_name="Doe",
            birth_date=date(1990, 1, 1),
            email="test@example.com",
            condition=models.ConditionEnum.ACTIVE,
            zip="12345",
            country="USA",
        )

        session.add(user)
        with pytest.raises(IntegrityError):
            session.commit()


class TestInterest:
    """Test class for Interest model.

    Tests interest creation and relationship validation.
    """

    def test_create_valid_interest(self, session: Session):
        """Test creating a valid interest with all required fields.

        Verifies that an interest can be created with all required
        fields and that the relationship to user is properly established.
        """
        user = models.User(
            last_name="Doe",
            first_name="John",
            birth_date=date(1990, 1, 1),
            email="john.doe.interest@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="123 Main St",
            city="Anytown",
            state_province="CA",
            zip="12345",
            country="USA",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        interest = models.Interest(
            user_id=user.id,
            interest_name="Reading",
            category="Hobbies",
            description="Love reading science fiction novels",
        )

        session.add(interest)
        session.commit()
        session.refresh(interest)

        assert interest.id is not None
        assert interest.user_id == user.id
        assert interest.interest_name == "Reading"
        assert interest.category == "Hobbies"
        assert interest.description == ("Love reading science fiction novels")
        assert interest.created_at is not None


class TestDislike:
    """Test class for Dislike model.

    Tests dislike creation and relationship validation.
    """

    def test_create_valid_dislike(self, session: Session):
        """Test creating a valid dislike with all required fields.

        Verifies that a dislike can be created with all required
        fields and that the relationship to user is properly established.
        """
        user = models.User(
            last_name="Smith",
            first_name="Jane",
            birth_date=date(1985, 5, 15),
            email="jane.smith.dislike@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="456 Oak Ave",
            city="Somewhere",
            state_province="NY",
            zip="54321",
            country="USA",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        dislike = models.Dislike(
            user_id=user.id,
            dislike_name="Loud Noises",
            category="Sensory",
            severity="Moderate",
            description="Sensitive to loud sudden noises",
        )

        session.add(dislike)
        session.commit()
        session.refresh(dislike)

        assert dislike.id is not None
        assert dislike.user_id == user.id
        assert dislike.dislike_name == "Loud Noises"
        assert dislike.category == "Sensory"
        assert dislike.severity == "Moderate"
        assert dislike.description == ("Sensitive to loud sudden noises")
        assert dislike.created_at is not None

    def test_create_dislike_without_required_fields(self, session: Session):
        """Test creating a dislike without required fields (should fail).

        Verifies that required field constraints are enforced
        and dislikes cannot be created without essential information.
        """
        dislike = models.Dislike(
            category="Test",
            severity="Mild",
        )

        session.add(dislike)
        with pytest.raises(IntegrityError):
            session.commit()


class TestAllergy:
    """Test class for Allergy model.

    Tests allergy creation and constraint validation.
    """

    def test_create_valid_allergy(self, session: Session):
        """Test creating a valid allergy with all required fields.

        Verifies that an allergy can be created with all required
        fields and that the name is properly assigned.
        """
        allergy = models.Allergy(
            name="Peanut Allergy",
            description=("Severe allergic reaction to peanuts and peanut products"),
        )

        session.add(allergy)
        session.commit()
        session.refresh(allergy)

        assert allergy.name == "Peanut Allergy"
        assert allergy.description == (
            "Severe allergic reaction to peanuts and peanut products"
        )


class TestProduct:
    """Test class for Product model.

    Tests product creation and validation.
    """

    def test_create_valid_product(self, session: Session):
        """Test creating a valid product with all required fields.

        Verifies that a product can be created with all required
        fields and that the UUID is properly assigned.
        """
        product = models.Product(
            name="Organic Apples",
            description="Fresh organic apples from local farms",
            price=4.99,
            quantity=100,
            image_url="https://example.com/apples.jpg",
            category="Fruits",
            sub_category="Organic",
            brand="Local Farms",
            is_active=True,
        )

        session.add(product)
        session.commit()
        session.refresh(product)

        assert product.id is not None
        assert product.name == "Organic Apples"
        assert product.description == ("Fresh organic apples from local farms")
        assert product.price == 4.99
        assert product.quantity == 100
        assert product.image_url == "https://example.com/apples.jpg"
        assert product.category == "Fruits"
        assert product.sub_category == "Organic"
        assert product.brand == "Local Farms"
        assert product.is_active is True
        assert product.created_at is not None
        assert product.updated_at is not None

    def test_create_product_with_negative_price(self, session: Session):
        """Test creating a product with negative price.

        Verifies that products can have negative prices
        (though this might not be desired in production).
        """
        product = models.Product(
            name="Invalid Product",
            description="Product with negative price",
            price=-10.00,
            quantity=50,
            category="Test",
            sub_category="Test",
            brand="Test Brand",
        )

        session.add(product)
        session.commit()
        session.refresh(product)
        assert product.price == -10.00


class TestOrder:
    """Test class for Order model.

    Tests order creation and validation.
    """

    def test_create_valid_order(self, session: Session):
        """Test creating a valid order with all required fields.

        Verifies that an order can be created with all required
        fields and that the relationship to user is properly established.
        """
        user = models.User(
            last_name="Johnson",
            first_name="Bob",
            birth_date=date(1980, 3, 20),
            email="bob.johnson@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="789 Pine St",
            city="Springfield",
            state_province="IL",
            zip="62701",
            country="USA",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        order = models.Order(
            user_id=user.id,
            total_amount=Decimal("29.99"),
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        assert order.id is not None
        assert order.user_id == user.id
        assert order.total_amount == Decimal("29.99")
        assert order.checked_out is False
        assert order.created_at is not None
        assert order.updated_at is not None

    def test_create_order_with_checked_out_status(self, session):
        """Test creating an order with checked_out status.

        Verifies that orders can be created with different
        checked_out values.
        """
        user = models.User(
            last_name="Wilson",
            first_name="Alice",
            birth_date=date(1995, 7, 10),
            email="alice.wilson@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="321 Elm St",
            city="Riverside",
            state_province="CA",
            zip="92501",
            country="USA",
        )

        session.add(user)
        session.commit()
        session.refresh(user)

        order = models.Order(
            user_id=user.id,
            total_amount=Decimal("15.50"),
            checked_out=True,
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        assert order.checked_out is True


class TestPurchase:
    """Test class for Purchase model.

    Tests purchase creation and relationship validation.
    """

    def test_create_valid_purchase(self, session):
        """Test creating a valid purchase with all required fields.

        Verifies that a purchase can be created with all required
        fields and that all relationships are properly established.
        """
        user = models.User(
            last_name="Davis",
            first_name="Charlie",
            birth_date=date(1988, 12, 5),
            email="charlie.davis@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="654 Maple Ave",
            city="Oakland",
            state_province="CA",
            zip="94601",
            country="USA",
        )

        product = models.Product(
            name="Organic Bananas",
            description="Fresh organic bananas",
            price=2.99,
            quantity=200,
            category="Fruits",
            sub_category="Organic",
            brand="Tropical Farms",
        )

        session.add(user)
        session.add(product)
        session.commit()
        session.refresh(user)
        session.refresh(product)

        order = models.Order(
            user_id=user.id,
            total_amount=Decimal("5.98"),
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        purchase = models.Purchase(
            order_id=order.id,
            user_id=user.id,
            product_id=product.id,
            quantity=2,
            total_amount=Decimal("5.98"),
            status=models.OrderStatus.IN_CART,
        )

        session.add(purchase)
        session.commit()
        session.refresh(purchase)

        assert purchase.id is not None
        assert purchase.order_id == order.id
        assert purchase.user_id == user.id
        assert purchase.product_id == product.id
        assert purchase.quantity == 2
        assert purchase.total_amount == Decimal("5.98")
        assert purchase.status == models.OrderStatus.IN_CART
        assert purchase.created_at is not None

    def test_create_purchase_with_different_statuses(self, session: Session):
        """Test creating purchases with different status values.

        Verifies that all order status enum values can be used
        when creating purchases.
        """
        user = models.User(
            last_name="Brown",
            first_name="David",
            birth_date=date(1992, 4, 15),
            email="david.brown@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="987 Cedar Ln",
            city="Portland",
            state_province="OR",
            zip="97201",
            country="USA",
        )

        product = models.Product(
            name="Test Product",
            description="Test product description",
            price=10.00,
            quantity=50,
            category="Test",
            sub_category="Test",
            brand="Test Brand",
        )

        session.add(user)
        session.add(product)
        session.commit()
        session.refresh(user)
        session.refresh(product)

        order = models.Order(
            user_id=user.id,
            total_amount=Decimal("10.00"),
        )

        session.add(order)
        session.commit()
        session.refresh(order)

        statuses = [
            models.OrderStatus.IN_CART,
            models.OrderStatus.PURCHASED,
            models.OrderStatus.REFUNDED,
            models.OrderStatus.SHIPPED,
            models.OrderStatus.CANCELLED,
            models.OrderStatus.COMPLETED,
        ]

        for status in statuses:
            purchase = models.Purchase(
                order_id=order.id,
                user_id=user.id,
                product_id=product.id,
                quantity=1,
                total_amount=Decimal("10.00"),
                status=status,
            )

            session.add(purchase)
            session.commit()
            session.refresh(purchase)

            assert purchase.status == status

    def test_create_purchase_with_invalid_order_id(self, session):
        """Test creating a purchase with invalid order_id (should fail).

        Verifies that foreign key constraints are enforced
        and purchases cannot be created without valid order references.
        """
        user = models.User(
            last_name="Brown",
            first_name="David",
            birth_date=date(1992, 4, 15),
            email="david.brown@example.com",
            condition=models.ConditionEnum.ACTIVE,
            street1="987 Cedar Ln",
            city="Portland",
            state_province="OR",
            zip="97201",
            country="USA",
        )

        product = models.Product(
            name="Test Product",
            description="Test product description",
            price=10.00,
            quantity=50,
            category="Test",
            sub_category="Test",
            brand="Test Brand",
        )

        purchase = models.Purchase(
            order_id=99999,
            user_id=user.id,
            product_id=product.id,
            quantity=1,
            total_amount=Decimal("10.00"),
        )

        session.add(user)
        session.add(product)
        session.commit()
        session.refresh(user)
        session.refresh(product)

        session.add(purchase)
        with pytest.raises(IntegrityError):
            session.commit()
