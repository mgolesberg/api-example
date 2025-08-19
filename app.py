"""Collects all the API routes and sets properties to connect
to the database through Postgres.

This module serves as the main entry point for the FastAPI application,
configuring the main app instance and including all route modules.

Attributes
----------
app : fastapi.FastAPI
    The main FastAPI application instance with title "Example API"

Notes
-----
The application follows REST philosophy principles:
- URLs represent resources
- HTTP methods represent actions on those resources
- Resource identity belongs in the URL
- Resource representation belongs in the body
"""
from fastapi import FastAPI
from src.routes.interest import router as interest_router
from src.routes.dislike import router as dislike_router
from src.routes.product import router as product_router

from src.routes.user import router as user_router
from src.routes.allergy import router as allergy_router
from src.routes.order_and_purchase import router as order_and_purchase_router

app = FastAPI(
    title="Example API",
)

app.include_router(user_router)
app.include_router(allergy_router)
app.include_router(interest_router)
app.include_router(dislike_router)
app.include_router(product_router)
app.include_router(order_and_purchase_router)
