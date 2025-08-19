"""Product management routes and CRUD operations.

This module provides API endpoints for managing product information including
creation, updates, deletion, and retrieval. It extends the base CRUD class
with product-specific functionality.

Classes
-------
CRUD : BaseCRUD
    Extended CRUD class with product-specific operations

Functions
---------
as_dict : dict
    Convert product model to dictionary
get_products : list[Product]
    Retrieve all products
get_product : Product
    Retrieve a specific product by ID
create_product : Product
    Create a new product
update_product : Product
    Update product information
delete_product : Product
    Delete an existing product
"""

from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from src.db.models import Product
from src.routes.base_crud import BaseCRUD
from src.db.db import get_session


class CRUD(BaseCRUD):
    """Extended CRUD class for product-specific operations.

    Provides product management functionality including UUID-based lookups
    and specialized update operations.

    Methods
    -------
    update : Product
        Update product information by UUID
    """

    def update(  # pylint: disable=W0237
        self, session: Session, uuid: str, data: dict
    ) -> Product:
        """Update/Put a product by its UUID.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        uuid : str
            UUID string of the product to update
        data : dict
            Dictionary containing field names and values to update

        Returns
        -------
        Product
            The updated product object

        Raises
        ------
        HTTPException
            If no product is found or there's an integrity error
        """
        try:
            statement = select(self.model).where(self.model.id == UUID(uuid))
            result = session.exec(statement).first()
            if not result:
                raise HTTPException(status_code=404, detail="Record not found")
            data["id"] = UUID(uuid)
            for key, value in data.items():
                if value is not None:
                    setattr(result, key, value)
            session.add(result)
            session.commit()
            session.refresh(result)
            return result
        except IntegrityError as e:
            raise HTTPException(status_code=422, detail=f"Integrity error: {e}") from e


product_CRUD = CRUD(Product)

router = APIRouter(prefix="/product", tags=["Product"])


def as_dict(product: Product) -> dict:
    """Convert product model to dictionary.

    Parameters
    ----------
    product : Product
        Product model instance to convert

    Returns
    -------
    dict
        Dictionary representation of the product
    """
    return product.model_dump()


@router.get("/", response_model=list[Product])
async def get_products(session: Session = Depends(get_session)) -> list[Product]:
    """Get all products.

    Parameters
    ----------
    session : Session
        Database session dependency

    Returns
    -------
    list[Product]
        List of all product objects in the system
    """
    return product_CRUD.get_multiple(session)


@router.get("/{product_id}", response_model=Product)
async def get_product(
    product_id: str, session: Session = Depends(get_session)
) -> Product:
    """Get a product by ID.

    Parameters
    ----------
    product_id : str
        UUID string of the product to retrieve
    session : Session
        Database session dependency

    Returns
    -------
    Product
        The found product object
    """
    return product_CRUD.get(session, product_id)


@router.post("/", response_model=Product)
async def create_product(
    product_data: Product, session: Session = Depends(get_session)
) -> Product:
    """Create a new product.

    Parameters
    ----------
    product_data : Product
        Product data for creation
    session : Session
        Database session dependency

    Returns
    -------
    Product
        The created product object
    """
    return product_CRUD.create(session, product_data)


@router.put("/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_data: Annotated[dict, Depends(as_dict)],
    session: Session = Depends(get_session),
) -> Product:
    """Update an existing product with fields passed in the request body.

    The user can pass as few as one field to update.
    Others fields retain their existing values.

    Parameters
    ----------
    product_id : str
        UUID string of the product to update
    product_data : dict
        Dictionary containing fields to update
    session : Session
        Database session dependency

    Returns
    -------
    Product
        The updated product object
    """
    return product_CRUD.update(session, product_id, product_data)


@router.delete("/{product_id}", response_model=Product)
async def delete_product(
    product_id: str, session: Session = Depends(get_session)
) -> Product:
    """Delete an existing product.

    Parameters
    ----------
    product_id : str
        UUID string of the product to delete
    session : Session
        Database session dependency

    Returns
    -------
    Product
        The deleted product object
    """
    return product_CRUD.delete(session, product_id)
