"""Some AI written example data for testing and development purposes.

This module contains predefined test data for all database models including
users, interests, dislikes, allergies, products, orders, and purchases.
The data is designed to provide realistic examples for testing the API
endpoints and database operations.

Data Sets
---------
TEST_USERS : list[dict]
    Sample user data with various conditions and demographics
TEST_INTERESTS : list[dict]
    Sample user interest data with categories and descriptions
TEST_DISLIKES : list[dict]
    Sample user dislike data with severity levels
TEST_ALLERGIES : list[dict]
    Predefined list of common allergies with descriptions
TEST_USER_ALLERGIES : list[dict]
    Sample user-allergy relationship data
TEST_PRODUCTS : list[dict]
    Sample product data with various categories and prices
TEST_ORDERS : list[dict]
    Sample order data representing shopping cart states
TEST_PURCHASES : list[dict]
    Sample purchase data for individual items within orders

Notes
-----
All data uses realistic values and follows the constraints defined
in the database models. UUIDs are predefined for consistent testing.
"""

from datetime import date
from decimal import Decimal
import uuid
from src.db.models import (
    ConditionEnum,
    OrderStatus,
)

TEST_USERS = [
    {
        "last_name": "Smith",
        "first_name": "John",
        "birth_date": date(1990, 5, 15),
        "email": "john.smith@email.com",
        "phone_number": "+1234567890",
        "condition": ConditionEnum.ACTIVE,
        "street1": "123 Main Street",
        "street2": "Apt 4B",
        "city": "New York",
        "state_province": "NY",
        "zip": "10001",
        "country": "USA",
    },
    {
        "last_name": "Johnson",
        "first_name": "Sarah",
        "birth_date": date(1985, 8, 22),
        "email": "sarah.johnson@email.com",
        "phone_number": "+1987654321",
        "condition": ConditionEnum.ACTIVE,
        "street1": "456 Oak Avenue",
        "street2": None,
        "city": "Los Angeles",
        "state_province": "CA",
        "zip": "90210",
        "country": "USA",
    },
    {
        "last_name": "Williams",
        "first_name": "Michael",
        "birth_date": date(1992, 3, 10),
        "email": "michael.williams@email.com",
        "phone_number": "+1555123456",
        "condition": ConditionEnum.ACTIVE,
        "street1": "789 Pine Road",
        "street2": "Unit 12",
        "city": "Chicago",
        "state_province": "IL",
        "zip": "60601",
        "country": "USA",
    },
    {
        "last_name": "Brown",
        "first_name": "Emily",
        "birth_date": date(1988, 11, 30),
        "email": "emily.brown@email.com",
        "phone_number": "+1444333222",
        "condition": ConditionEnum.DEACTIVATED,
        "street1": "321 Elm Street",
        "street2": None,
        "city": "Houston",
        "state_province": "TX",
        "zip": "77001",
        "country": "USA",
    },
    {
        "last_name": "Davis",
        "first_name": "David",
        "birth_date": date(1995, 7, 4),
        "email": "david.davis@email.com",
        "phone_number": "+1666777888",
        "condition": ConditionEnum.ACTIVE,
        "street1": "654 Maple Drive",
        "street2": "Suite 200",
        "city": "Phoenix",
        "state_province": "AZ",
        "zip": "85001",
        "country": "USA",
    },
]

TEST_INTERESTS = [
    {
        "user_id": 1,
        "interest_name": "Technology",
        "category": "Hobbies",
        "description": "Passionate about latest tech gadgets and innovations",
    },
    {
        "user_id": 1,
        "interest_name": "Running",
        "category": "Sports",
        "description": "Marathon training and fitness enthusiast",
    },
    {
        "user_id": 2,
        "interest_name": "Cooking",
        "category": "Lifestyle",
        "description": "Enjoys experimenting with new recipes",
    },
    {
        "user_id": 2,
        "interest_name": "Travel",
        "category": "Lifestyle",
        "description": "Loves exploring new destinations",
    },
    {
        "user_id": 3,
        "interest_name": "Music",
        "category": "Entertainment",
        "description": "Plays guitar and enjoys various genres",
    },
    {
        "user_id": 4,
        "interest_name": "Reading",
        "category": "Entertainment",
        "description": "Avid reader of science fiction and fantasy",
    },
    {
        "user_id": 5,
        "interest_name": "Photography",
        "category": "Arts",
        "description": "Landscape and street photography enthusiast",
    },
]

TEST_DISLIKES = [
    {
        "user_id": 1,
        "dislike_name": "Spicy Food",
        "category": "Food",
        "severity": "Severe",
        "description": "Cannot tolerate hot spices",
    },
    {
        "user_id": 2,
        "dislike_name": "Cold Weather",
        "category": "Weather",
        "severity": "Moderate",
        "description": "Prefers warm climates",
    },
    {
        "user_id": 3,
        "dislike_name": "Crowded Places",
        "category": "Environment",
        "severity": "Mild",
        "description": "Avoids large crowds and busy areas",
    },
    {
        "user_id": 4,
        "dislike_name": "Early Mornings",
        "category": "Lifestyle",
        "severity": "Moderate",
        "description": "Not a morning person",
    },
    {
        "user_id": 5,
        "dislike_name": "Public Speaking",
        "category": "Social",
        "severity": "Severe",
        "description": "Gets nervous in front of large groups",
    },
]

# Predefined list of allergies
TEST_ALLERGIES = [
    {
        "name": "Milk",
        "description": "Allergic reaction to milk and dairy products",
    },
    {
        "name": "Eggs",
        "description": "Allergic reaction to eggs and egg products",
    },
    {
        "name": "Fish",
        "description": "Allergic reaction to fish and fish products",
    },
    {
        "name": "Shellfish",
        "description": "Allergic reaction to shellfish and crustaceans",
    },
    {
        "name": "Tree Nuts",
        "description": "Allergic reaction to tree nuts (almonds, walnuts, etc.)",
    },
    {
        "name": "Peanuts",
        "description": "Allergic reaction to peanuts and peanut products",
    },
    {
        "name": "Wheat",
        "description": "Allergic reaction to wheat and wheat products",
    },
    {
        "name": "Soybeans",
        "description": "Allergic reaction to soybeans and soy products",
    },
    {
        "name": "Sesame",
        "description": "Allergic reaction to sesame seeds and sesame products",
    },
    {
        "name": "Nightshade",
        "description": (
            "Allergic reaction to nightshade vegetables "
            "(tomatoes, potatoes, peppers, eggplant)"
        ),
    },
]

# User-Allergy relationships
TEST_USER_ALLERGIES = [
    {
        "user_id": 1,
        "allergy_name": "Milk",
        "notes": "Lactose intolerance and mild dairy allergy",
    },
    {
        "user_id": 2,
        "allergy_name": "Eggs",
        "notes": "Allergic reaction to eggs - must avoid completely",
    },
    {
        "user_id": 3,
        "allergy_name": "Shellfish",
        "notes": "Minor skin reaction to shellfish",
    },
    {
        "user_id": 4,
        "allergy_name": "Wheat",
        "notes": "Celiac disease - must avoid all wheat products",
    },
    {
        "user_id": 5,
        "allergy_name": "Peanuts",
        "notes": "Anaphylactic reaction - must avoid completely",
    },
    {
        "user_id": 1,
        "allergy_name": "Soybeans",
        "notes": "Minor soy allergy",
    },
    {
        "user_id": 3,
        "allergy_name": "Tree Nuts",
        "notes": "Severe reaction to tree nuts",
    },
]

TEST_PRODUCTS = [
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),
        "name": "Wireless Bluetooth Headphones",
        "description": ("High-quality wireless headphones with noise cancellation"),
        "price": 129.99,
        "quantity": 50,
        "image_url": "images/hightech_ears.webp",
        "category": "Electronics",
        "sub_category": "Audio",
        "brand": "TechSound",
        "is_active": True,
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),
        "name": "Smartphone Case",
        "description": "Durable protective case for iPhone 15",
        "price": 24.99,
        "quantity": 100,
        "image_url": "images/iphone_case.jpg",
        "category": "Accessories",
        "sub_category": "Phone Cases",
        "brand": "ProtectPro",
        "is_active": True,
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440003"),
        "name": "Coffee Maker",
        "description": "Programmable coffee maker with thermal carafe",
        "price": 89.99,
        "quantity": 25,
        "image_url": "images/coffee_maker.jpg",
        "category": "Home & Kitchen",
        "sub_category": "Appliances",
        "brand": "BrewMaster",
        "is_active": True,
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440004"),
        "name": "Running Shoes",
        "description": "Lightweight running shoes for daily training",
        "price": 79.99,
        "quantity": 75,
        "image_url": "images/running_shoes.jpg",
        "category": "Sports",
        "sub_category": "Footwear",
        "brand": "RunFast",
        "is_active": True,
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440005"),
        "name": "Laptop Stand",
        "description": "Adjustable aluminum laptop stand for ergonomic setup",
        "price": 39.99,
        "quantity": 60,
        "image_url": "images/laptop_stand.jpeg",
        "category": "Electronics",
        "sub_category": "Computer Accessories",
        "brand": "ErgoTech",
        "is_active": True,
    },
    {
        "id": uuid.UUID("550e8400-e29b-41d4-a716-446655440006"),
        "name": "Discontinued Product",
        "description": "This product is no longer available",
        "price": 19.99,
        "quantity": 0,
        "image_url": None,
        "category": "Test",
        "sub_category": "Discontinued",
        "brand": "TestBrand",
        "is_active": False,
    },
]

# Orders represent complete checkouts
TEST_ORDERS = [
    {
        "user_id": 1,
        "total_amount": Decimal("284.97"),  # 2 headphones + 1 case
        "checked_out": True,
    },
    {
        "user_id": 2,
        "total_amount": Decimal("24.99"),  # 1 case
        "checked_out": True,
    },
    {
        "user_id": 3,
        "total_amount": Decimal("89.99"),  # 1 coffee maker
        "checked_out": False,
    },
    {
        "user_id": 4,
        "total_amount": Decimal("169.98"),  # 1 headphones + 1 laptop stand
        "checked_out": True,
    },
    {
        "user_id": 5,
        "total_amount": Decimal("39.99"),  # 1 laptop stand
        "checked_out": False,
    },
]

# Purchases represent individual items within each order
TEST_PURCHASES = [
    # Order 1: John's order (2 headphones + 1 case)
    {
        "order_id": 1,
        "user_id": 1,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),  # Headphones
        "quantity": 2,
        "unit_price": Decimal("129.99"),
        "total_amount": Decimal("259.98"),
        "status": OrderStatus.COMPLETED,
    },
    {
        "order_id": 1,
        "user_id": 1,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),  # Case
        "quantity": 1,
        "unit_price": Decimal("24.99"),
        "total_amount": Decimal("24.99"),
        "status": OrderStatus.COMPLETED,
    },
    # Order 2: Sarah's order (1 case)
    {
        "order_id": 2,
        "user_id": 2,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440002"),  # Case
        "quantity": 1,
        "unit_price": Decimal("24.99"),
        "total_amount": Decimal("24.99"),
        "status": OrderStatus.COMPLETED,
    },
    # Order 3: Michael's order (1 coffee maker)
    {
        "order_id": 3,
        "user_id": 3,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440003"),  # Coffee Maker
        "quantity": 1,
        "unit_price": Decimal("89.99"),
        "total_amount": Decimal("89.99"),
        "status": OrderStatus.IN_CART,
    },
    # Order 4: Emily's order (1 headphones + 1 laptop stand)
    {
        "order_id": 4,
        "user_id": 4,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440001"),  # Headphones
        "quantity": 1,
        "unit_price": Decimal("129.99"),
        "total_amount": Decimal("129.99"),
        "status": OrderStatus.COMPLETED,
    },
    {
        "order_id": 4,
        "user_id": 4,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440005"),  # Laptop Stand
        "quantity": 1,
        "unit_price": Decimal("39.99"),
        "total_amount": Decimal("39.99"),
        "status": OrderStatus.COMPLETED,
    },
    # Order 5: David's order (1 laptop stand) - CANCELLED
    {
        "order_id": 5,
        "user_id": 5,
        "product_id": uuid.UUID("550e8400-e29b-41d4-a716-446655440005"),  # Laptop Stand
        "quantity": 1,
        "unit_price": Decimal("39.99"),
        "total_amount": Decimal("39.99"),
        "status": OrderStatus.CANCELLED,
    },
]
