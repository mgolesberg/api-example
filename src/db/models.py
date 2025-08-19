# next step is dockerizing the database
"""Database models and SQLModel definitions for the API.

This module contains all the database models using SQLModel, which combines
SQLAlchemy and Pydantic. It defines the structure for users, products,
orders, purchases, interests, dislikes, and allergies.

Classes
-------
ConditionEnum : enum.Enum
    Enumeration for user account conditions
OrderStatus : enum.Enum
    Enumeration for order and purchase statuses
UserAllergy : SQLModel
    Associative table for many-to-many user-allergy relationships
User : SQLModel
    Main user model with personal and address information
Interest : SQLModel
    Model representing user interests and preferences
Dislike : SQLModel
    Model representing user dislikes and aversions
Allergy : SQLModel
    Model representing predefined allergy options
Product : SQLModel
    Model representing products available for purchase
OrderBase : SQLModel
    Base model for order creation and updates
Order : SQLModel
    Model representing a bundle of items for checkout
PurchaseBase : SQLModel
    Base model for purchase creation and updates
Purchase : SQLModel
    Model representing individual items within an order
"""
import enum
import uuid
from decimal import Decimal
from datetime import date, datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import CheckConstraint, Enum


# Enum definitions for PostgreSQL
class ConditionEnum(enum.Enum):
    """Condition enum for user status.

    Defines the possible states a user account can be in.

    Attributes
    ----------
    ACTIVE : str
        User account is active and functional
    DEACTIVATED : str
        User account is temporarily disabled
    MARKED_FOR_DELETION : str
        User account is scheduled for permanent removal
    TEST : str
        User account is for testing purposes
    NO_LONGER_IN_STOCK : str
        User account is no longer available (legacy)
    """

    ACTIVE = "Active"
    DEACTIVATED = "Deactivated"
    MARKED_FOR_DELETION = "Marked for deletion"
    TEST = "Test"
    NO_LONGER_IN_STOCK = "No longer in stock"


class OrderStatus(enum.Enum):
    """Order status enum for tracking order lifecycle.

    Defines the possible states an order or purchase can be in.

    Attributes
    ----------
    IN_CART : str
        Item is in user's shopping cart
    PURCHASED : str
        Order has been purchased but not yet processed
    REFUNDED : str
        Order has been refunded to customer
    SHIPPED : str
        Order has been shipped to customer
    CANCELLED : str
        Order has been cancelled
    COMPLETED : str
        Order has been successfully delivered
    """

    IN_CART = "In cart"
    PURCHASED = "Purchased"
    REFUNDED = "Refunded"
    SHIPPED = "Shipped"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"


class UserAllergy(SQLModel, table=True):
    """Associative table for many-to-many relationship between users and allergies.

    This table links users to their allergies, allowing for flexible
    allergy management and tracking.

    Attributes
    ----------
    user_id : int
        Foreign key reference to the user table
    allergy_name : str
        Foreign key reference to the allergy table
    notes : str | None
        Optional notes about the specific allergy for this user
    """

    __tablename__ = "user_allergy"

    user_id: int = Field(foreign_key="user.id", index=True, primary_key=True)
    allergy_name: str = Field(foreign_key="allergy.name", index=True, primary_key=True)
    notes: str | None = None


class User(SQLModel, table=True):
    """User model representing application users.

    Stores comprehensive user information including personal details,
    contact information, address, and account status.

    Attributes
    ----------
    id : int | None
        Primary key, auto-generated
    last_name : str
        User's last name
    first_name : str
        User's first name
    birth_date : date
        User's date of birth
    email : str
        User's email address (unique)
    phone_number : str | None
        User's phone number in E.164 format
    condition : ConditionEnum
        Current status of the user account
    street1 : str
        Primary street address
    street2 : str | None
        Secondary address information (apartment, unit, etc.)
    city : str
        City name
    state_province : str
        State or province
    zip : str
        ZIP or postal code
    country : str
        Country name

    Notes
    -----
    Phone number validation uses E.164 format regex pattern.
    Email addresses must be unique across all users.
    """

    __tablename__ = "user"

    id: int | None = Field(default=None, primary_key=True)

    last_name: str
    first_name: str
    birth_date: date

    email: str = Field(sa_column_kwargs={"unique": True})
    phone_number: str | None = None

    condition: ConditionEnum = Field(
        sa_column=Enum(
            ConditionEnum,
            name="condition_enum",
            values_callable=lambda x: [e.value for e in x],
        )
    )

    street1: str
    street2: str | None = None
    city: str
    state_province: str
    zip: str
    country: str

    __table_args__ = (
        CheckConstraint(
            "phone_number ~ '^\\+?[1-9]\\d{1,14}$'", name="valid_phone_number"
        ),
    )

    # Relationships
    interests: list["Interest"] = Relationship(back_populates="user")
    dislikes: list["Dislike"] = Relationship(back_populates="user")
    allergies: list["Allergy"] = Relationship(
        back_populates="users", link_model=UserAllergy
    )
    orders: list["Order"] = Relationship(back_populates="user")
    purchases: list["Purchase"] = Relationship(back_populates="user")


class Interest(SQLModel, table=True):
    """Interest model representing user interests.

    Stores information about user interests and preferences,
    organized by category for better user experience.

    Attributes
    ----------
    id : int | None
        Primary key, auto-generated
    user_id : int
        Foreign key reference to the user table
    interest_name : str
        Name or title of the interest
    category : str | None
        Category classification for the interest
    description : str | None
        Detailed description of the interest
    created_at : datetime
        Timestamp when the interest was recorded
    """

    __tablename__ = "interest"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    interest_name: str
    category: str | None = None
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    user: User = Relationship(back_populates="interests")


class Dislike(SQLModel, table=True):
    """Dislike model representing user dislikes.

    Stores information about user dislikes and aversions,
    including severity levels for better understanding.

    Attributes
    ----------
    id : int | None
        Primary key, auto-generated
    user_id : int
        Foreign key reference to the user table
    dislike_name : str
        Name or title of the dislike
    category : str | None
        Category classification for the dislike
    severity : str | None
        Severity level of the dislike
    description : str | None
        Detailed description of the dislike
    created_at : datetime
        Timestamp when the dislike was recorded
    """

    __tablename__ = "dislike"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    dislike_name: str
    category: str | None = None
    severity: str | None = None
    description: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)

    user: User = Relationship(back_populates="dislikes")


class Allergy(SQLModel, table=True):
    """Allergy model representing predefined allergy options.

    Stores a predefined list of common allergies that users
    can select from, ensuring consistency in allergy tracking.

    Attributes
    ----------
    name : str | None
        Primary key, name of the allergy
    description : str | None
        Detailed description of the allergy
    """

    __tablename__ = "allergy"

    name: str | None = Field(default=None, primary_key=True)
    description: str | None = None

    users: list[User] = Relationship(back_populates="allergies", link_model=UserAllergy)


class Product(SQLModel, table=True):
    """Product model representing items available for purchase.

    Stores comprehensive product information including pricing,
    inventory, categorization, and availability status.

    Attributes
    ----------
    id : uuid.UUID | None
        Primary key, auto-generated UUID
    name : str
        Product name
    description : str
        Detailed product description
    price : float
        Product price in currency units
    quantity : int
        Available inventory quantity
    image_url : str | None
        URL to product image
    category : str
        Main product category
    sub_category : str
        Sub-category classification
    brand : str
        Product brand name
    is_active : bool
        Whether the product is currently available
    created_at : datetime
        Timestamp when product was added
    updated_at : datetime
        Timestamp when product was last updated
    """

    __tablename__ = "product"

    id: uuid.UUID | None = Field(default_factory=uuid.uuid4, primary_key=True)

    name: str
    description: str
    price: float
    quantity: int
    image_url: str | None = None
    category: str
    sub_category: str
    brand: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class OrderBase(SQLModel):
    """Simplified order model for the API.

    Base model containing essential order fields for API operations.

    Attributes
    ----------
    id : int | None
        Primary key, auto-generated
    user_id : int
        Foreign key reference to the user table
    """

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)


class Order(OrderBase, table=True):
    """Order model representing a bundle of items for a user to checkout.

    Manages the shopping cart and checkout process, tracking
    total amounts and order status.

    Attributes
    ----------
    total_amount : Decimal
        Total cost of all items in the order
    created_at : datetime
        Timestamp when order was created
    updated_at : datetime
        Timestamp when order was last updated
    checked_out : bool
        Whether the order has been checked out
    """

    __tablename__ = "order"

    total_amount: Decimal = Field(decimal_places=2)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    checked_out: bool = False

    user: User = Relationship(back_populates="orders")
    purchases: list["Purchase"] = Relationship(back_populates="order")


class PurchaseBase(SQLModel):
    """Simplified purchase model for the API.

    Base model containing essential purchase fields for API operations.

    Attributes
    ----------
    id : int | None
        Primary key, auto-generated
    product_id : uuid.UUID
        Foreign key reference to the product table
    user_id : int
        Foreign key reference to the user table
    quantity : int
        Quantity of the product to purchase
    """

    id: int | None = Field(default=None, primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    quantity: int = 1


class Purchase(PurchaseBase, table=True):
    """Purchase model representing individual items within an order.

    Tracks individual product purchases, including quantities,
    pricing, and status throughout the order lifecycle.

    Attributes
    ----------
    order_id : int
        Foreign key reference to the order table
    total_amount : Decimal
        Total cost for this specific purchase (quantity * unit price)
    status : OrderStatus
        Current status of the purchase
    created_at : datetime
        Timestamp when purchase was created
    updated_at : datetime
        Timestamp when purchase was last updated
    """

    __tablename__ = "purchase"

    order_id: int = Field(foreign_key="order.id", index=True)
    total_amount: Decimal = Field(decimal_places=2)
    status: OrderStatus = Field(
        default=OrderStatus.IN_CART,
        sa_column=Enum(
            OrderStatus,
            name="purchase_status_enum",
            values_callable=lambda x: [e.value for e in x],
        ),
    )
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    order: Order = Relationship(back_populates="purchases")
    product: Product = Relationship()
    user: User = Relationship(back_populates="purchases")
