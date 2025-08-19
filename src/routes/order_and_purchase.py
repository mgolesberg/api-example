"""
Order and purchase management routes.

This module provides API endpoints for managing shopping cart functionality,
order creation, and purchase management. It handles the complete lifecycle
of orders from cart creation to checkout.

Classes
-------
OrderPurchaseResponse : BaseModel
    Response model containing order and associated purchases
buyCRUD : BaseCRUD
    CRUD operations for order and purchase management

Functions
---------
get_order : list[OrderPurchaseResponse]
    Retrieve all orders for a user
create_purchase : OrderPurchaseResponse
    Create a new purchase and add to cart
update_purchase_quantity : OrderPurchaseResponse
    Update quantity of items in cart
delete_purchase : OrderPurchaseResponse
    Remove items from cart by setting quantity to 0
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError, DataError

from src.db.models import (
    PurchaseBase,
    Order,
    Purchase,
    OrderStatus,
    Product,
)
from src.routes.base_crud import BaseCRUD
from src.db.db import get_session


# Custom response model for the create_order endpoint
class OrderPurchaseResponse(BaseModel):
    """Response model for order and purchase operations.

    Contains the order information along with all associated purchases.

    Attributes
    ----------
    order : Order
        The order object with metadata
    purchases : list[Purchase]
        List of all purchases associated with the order
    """

    order: Order
    purchases: list[Purchase]


class BuyCRUD(BaseCRUD):
    """CRUD operations for order and purchase management.

    Extends BaseCRUD to provide specialized methods for handling
    shopping cart operations, order creation, and purchase updates.

    Methods
    -------
    get : list[Order]
        Retrieve all orders for a user
    create_purchase : tuple[Order, list[Purchase]]
        Create a new purchase and manage cart state
    update_purchase_quantity : tuple[Order, list[Purchase]]
        Update quantities and manage cart totals
    """

    def get(  # pylint: disable=W0237
        self, session: Session, user_id: int
    ) -> list[Order]:
        """Retrieve all orders for a specific user.

        Returns all orders associated with the user, including both
        open (unchecked) and closed (checked out) orders.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        user_id : int
            The ID of the user to retrieve orders for

        Returns
        -------
        list[Order]
            List of all orders for the user
        """
        statement = select(Order).where(Order.user_id == user_id)
        orders = session.exec(statement).all()
        return orders

    def create_purchase(
        self, session: Session, purchase_base: PurchaseBase
    ) -> tuple[Order, list[Purchase]]:
        """Create an order from the first purchase added into the cart.

        First, we transfer our smaller models into dictionaries to accumulate the data.
        Then, we use the dictionaries to instantiate the full model objects.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        purchase_base : PurchaseBase
            Base purchase data containing product, user, and quantity

        Returns
        -------
        tuple[Order, list[Purchase]]
            Tuple containing the order and list of purchases

        Raises
        ------
        HTTPException
            If product is not found or there are multiple open orders
        """
        purchase_dict = purchase_base.model_dump()
        purchase_dict["id"] = None
        purchase_dict["status"] = OrderStatus.IN_CART

        # Get product information
        statement = select(Product).where(Product.id == purchase_dict["product_id"])
        product = session.exec(statement).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        purchase_dict["total_amount"] = Decimal(
            str(round(product.price * purchase_dict["quantity"], 2))
        )

        # Check if we already have an open order for this user. If not, create one.
        statement = select(Order).where(
            Order.user_id == purchase_dict["user_id"],
            Order.checked_out == False,  # pylint: disable=C0121
        )
        orders = session.exec(statement).all()
        orders_count = len(list(orders))
        if orders_count > 1:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Multiple open orders found for user "
                    f"{purchase_dict['user_id']}"
                ),
            )
        order = orders[0] if orders_count > 0 else None
        try:
            purchase = Purchase(**purchase_dict)
            if not order:
                order_dict = {}
                order_dict["id"] = None
                order_dict["user_id"] = purchase_dict["user_id"]
                order_dict["checked_out"] = False
                order_dict["total_amount"] = purchase_dict["total_amount"]
                order = Order(purchases=[purchase], **order_dict)
                session.add(order)
            else:
                product_ids = [purchase.product_id for purchase in order.purchases]
                if purchase_dict["product_id"] in product_ids:
                    for purchase in order.purchases:
                        if purchase.product_id == purchase_dict["product_id"]:
                            purchase.quantity += purchase_dict["quantity"]
                            order.total_amount -= purchase.total_amount
                            purchase.total_amount = Decimal(
                                str(round(product.price * purchase.quantity, 2))
                            )
                            order.total_amount += purchase.total_amount
                            break
                else:
                    purchase_dict["order_id"] = order.id
                    purchase_dict["status"] = OrderStatus.IN_CART
                    order.purchases.append(purchase)
                    order.total_amount += purchase_dict["total_amount"]
                order.updated_at = datetime.now()
                session.add(order)
            session.commit()
            return order, order.purchases
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(
                status_code=422, detail=f"Integrity error: {str(e)}"
            ) from e
        except DataError as e:
            session.rollback()
            raise HTTPException(status_code=422, detail=f"Data error: {str(e)}") from e

    def update_purchase_quantity(
        self, session: Session, purchase_base: PurchaseBase
    ) -> tuple[Order, list[Purchase]]:
        """Update the quantity of a purchase in an open order.

        Handles quantity changes including positive increments, negative decrements,
        and removal of items when quantity becomes zero or negative. Also manages
        order totals and purchase lifecycle.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        purchase_base : PurchaseBase
            Base purchase data containing product, user, and quantity change

        Returns
        -------
        tuple[Order, list[Purchase]]
            Tuple containing the updated order and list of purchases

        Raises
        ------
        HTTPException
            If quantity change is 0, order is not found, purchase is not found,
            or there are multiple open orders
        """
        if purchase_base.quantity == 0:
            raise HTTPException(
                status_code=400,
                detail="Quantity change cannot be 0",
            )
        statement = select(Order).where(
            Order.user_id == purchase_base.user_id,
            Order.checked_out == False,  # pylint: disable=C0121
        )
        orders = session.exec(statement).all()
        orders_count = len(list(orders))
        if orders_count > 1:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Multiple open orders found for user " f"{purchase_base.user_id}"
                ),
            )
        order = orders[0] if orders_count > 0 else None
        if not order:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Order not found. Use a POST rather than a PUT "
                    "to create an order."
                ),
            )
        product_ids = [purchase.product_id for purchase in order.purchases]
        if purchase_base.product_id in product_ids:
            for purchase in order.purchases:
                if purchase.product_id == purchase_base.product_id:
                    product = purchase.product
                    purchase.quantity += purchase_base.quantity
                    purchase.updated_at = datetime.now()
                    if purchase.quantity <= 0:
                        order.total_amount -= purchase.total_amount
                        order.purchases.remove(purchase)
                        session.delete(purchase)
                        session.commit()
                        return order, order.purchases
                    order.total_amount -= purchase.total_amount
                    purchase.total_amount = Decimal(
                        str(round(product.price * purchase.quantity, 2))
                    )
                    order.total_amount += purchase.total_amount
                    break
        else:
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Product {purchase_base.product_id} not found "
                    f"in cart for user {purchase_base.user_id}"
                ),
            )
        try:
            order.updated_at = datetime.now()
            session.add(order)
            session.commit()
            return order, order.purchases
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(
                status_code=422, detail=f"Integrity error: {str(e)}"
            ) from e
        except DataError as e:
            session.rollback()
            raise HTTPException(status_code=422, detail=f"Data error: {str(e)}") from e

    def checkout(self, session: Session, user_id: int) -> tuple[Order, list[Purchase]]:
        """Checkout an open order for a user.

        Parameters
        ----------
        session : Session
            Database session to use for the operation
        user_id : int
            The ID of the user to checkout the order for

        Returns
        -------
        tuple[Order, list[Purchase]]
            Tuple containing the updated order and list of purchases
        """

        statement = select(Order).where(
            Order.user_id == user_id,
            Order.checked_out == False,  # pylint: disable=C0121
        )
        order = session.exec(statement).first()
        if not order:
            raise HTTPException(
                status_code=404,
                detail=f"No open order found for user {user_id}",
            )
        order.checked_out = True
        order.updated_at = datetime.now()
        session.add(order)
        for purchase in order.purchases:
            purchase.status = OrderStatus.PURCHASED
            purchase.updated_at = datetime.now()
            product = purchase.product
            if product.quantity < purchase.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=f"Not enough {product.name} in inventory",
                )
            product.quantity -= purchase.quantity
            product.updated_at = datetime.now()
            session.add(product)
        session.commit()
        return order, order.purchases


buy_CRUD = BuyCRUD(Order)


router = APIRouter(prefix="/buy", tags=["Order and Purchase"])


@router.get("/{user_id}", response_model=list[OrderPurchaseResponse])
async def get_order(
    user_id: int, session: Session = Depends(get_session)
) -> list[OrderPurchaseResponse]:
    """Get all orders for a user.

    Retrieves all orders associated with the user, including both
    open (unchecked) and closed (checked out) orders.

    Parameters
    ----------
    user_id : int
        The ID of the user to retrieve orders for
    session : Session
        Database session dependency

    Returns
    -------
    list[OrderPurchaseResponse]
        List of order responses with associated purchases
    """
    orders = buy_CRUD.get(session, user_id)
    return [
        OrderPurchaseResponse(order=order, purchases=order.purchases)
        for order in orders
    ]


@router.post("/", response_model=OrderPurchaseResponse)
async def create_purchase(
    purchase_base: PurchaseBase, session: Session = Depends(get_session)
) -> OrderPurchaseResponse:
    """Creates a purchase with a product.

    If there is an open order for the user, the purchase is added to the order.
    If there is no open order, a new order is created.

    Parameters
    ----------
    purchase_base : PurchaseBase
        The purchase data containing product, user, and quantity
    session : Session
        Database session dependency

    Returns
    -------
    OrderPurchaseResponse
        Response containing the order and associated purchases
    """
    order, purchases = buy_CRUD.create_purchase(session, purchase_base)
    return OrderPurchaseResponse(order=order, purchases=purchases)


@router.put("/", response_model=OrderPurchaseResponse)
async def update_purchase_quantity(
    purchase_base: PurchaseBase, session: Session = Depends(get_session)
) -> OrderPurchaseResponse:
    """Increment the quantity of a purchase in an open order.

    Parameters
    ----------
    purchase_base : PurchaseBase
        The purchase data containing product, user, and quantity change
    session : Session
        Database session dependency

    Returns
    -------
    OrderPurchaseResponse
        Response containing the updated order and associated purchases
    """
    order, purchases = buy_CRUD.update_purchase_quantity(session, purchase_base)
    return OrderPurchaseResponse(order=order, purchases=purchases)


@router.delete("/", response_model=OrderPurchaseResponse)
async def delete_purchase(
    product_id: UUID, user_id: int, session: Session = Depends(get_session)
) -> OrderPurchaseResponse:
    """Delete a purchase from an open order by setting its quantity to 0.

    Parameters
    ----------
    product_id : UUID
        The ID of the product to remove from the cart
    user_id : int
        The ID of the user whose cart to modify
    session : Session
        Database session dependency

    Returns
    -------
    OrderPurchaseResponse
        Response containing the updated order and associated purchases

    Raises
    ------
    HTTPException
        If the product is not found in the user's cart
    """
    statement = select(Purchase).where(
        Purchase.product_id == product_id, Purchase.user_id == user_id
    )
    purchase = session.exec(statement).first()
    if not purchase:
        raise HTTPException(
            status_code=404,
            detail=f"Product {product_id} not found in cart for user {user_id}",
        )
    remove_quantity = -1 * purchase.quantity
    order, purchases = buy_CRUD.update_purchase_quantity(
        session,
        PurchaseBase(quantity=remove_quantity, user_id=user_id, product_id=product_id),
    )
    return OrderPurchaseResponse(order=order, purchases=purchases)


@router.post("/checkout/{user_id}", response_model=OrderPurchaseResponse)
async def checkout(
    user_id: int, session: Session = Depends(get_session)
) -> OrderPurchaseResponse:
    """Checkout an open order for a user.

    Parameters
    ----------
    user_id : int
        The ID of the user to checkout the order for
    session : Session
        Database session dependency

    Returns
    -------
    OrderPurchaseResponse
        Response containing the updated order and associated purchases
    """
    order, purchases = buy_CRUD.checkout(session, user_id)
    return OrderPurchaseResponse(order=order, purchases=purchases)
