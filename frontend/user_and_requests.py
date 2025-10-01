"""
User and API Request Management Module.

This module provides comprehensive classes and functions for managing user data,
API interactions, and e-commerce functionality in the Streamlit frontend application.

Classes
-------
User
    Manages user profiles, interests, dislikes, and allergies.
OrderPurchase
    Handles order and purchase data retrieval and processing.
Product
    Manages product information and cart operations.

Functions
---------
get_all_users()
    Get all user IDs from the system.
get_all_products()
    Retrieve all products from the API.
get_all_product_ids()
    Get all product IDs from the API.
get_all_active_in_stock_products()
    Get all active products that are in stock.

"""
from uuid import UUID

import requests
import pandas as pd


class User:
    """
    A class to manage user data and API interactions.

    This class provides methods to interact with the user API endpoints,
    including managing user interests, dislikes, and allergies.

    Parameters
    ----------
    email : str
        The user's email address.
    user_id : int, optional
        The user's unique identifier. If not provided, it will be
        fetched from the API using the email address.

    Attributes
    ----------
    user_id : int
        The user's unique identifier.
    email : str
        The user's email address.
    base_url : str
        The base URL for API requests (default: "http://api:8000").
    """

    def __init__(
        self,
        email: str,
        user_id: int | None = None,
    ):
        self.user_id = user_id
        self.email = email
        self.base_url = "http://api:8000"

        if self.email and not self.user_id:
            self._fetch_user_id()

    def _fetch_user_id(self):
        """
        Fetch user_id from email if not already set.

        This private method makes an API call to retrieve the user's ID
        based on their email address. The user_id is then stored in the
        instance attribute.

        Notes
        -----
        This method is called automatically during initialization if
        user_id is not provided but email is available.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        if self.email:
            response = requests.get(f"{self.base_url}/user/{self.email}")
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get("id")

    def get_interests(self) -> list:
        """
        Get user interests from the API.

        Retrieves all interests associated with the user from the API
        and stores them in the instance's interests attribute.

        Returns
        -------
        list
            A list of dictionaries containing interest information.
            Each dictionary contains at least 'id' and 'interest_name' keys.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """

        response = requests.get(f"{self.base_url}/interest/{self.user_id}")
        response.raise_for_status()
        self.interests = response.json()
        return response.json()

    def add_interests(self, interest: str) -> dict:
        """
        Add a new interest for the user.

        Creates a new interest entry for the user via API call and
        refreshes the local interests list.

        Parameters
        ----------
        interest : str
            The name of the interest to add.

        Returns
        -------
        dict
            The response from the API containing the created interest data.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(
            f"{self.base_url}/interest/",
            json={"user_id": self.user_id, "interest_name": interest},
        )
        response.raise_for_status()
        self.interests = self.get_interests()
        return response.json()

    def delete_interests(self, interest_id: int) -> dict:
        """
        Delete a user interest by its ID.

        Removes an interest from the user's profile via API call and
        refreshes the local interests list.

        Parameters
        ----------
        interest_id : int
            The unique identifier of the interest to delete.

        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.delete(
            f"{self.base_url}/interest/{interest_id}",
        )
        response.raise_for_status()
        self.interests = self.get_interests()

    def get_dislikes(self) -> list:
        """
        Get user dislikes from the API.

        Retrieves all dislikes associated with the user from the API
        and stores them in the instance's dislikes attribute.

        Returns
        -------
        list
            A list of dictionaries containing dislike information.
            Each dictionary contains at least 'id' and 'dislike_name' keys.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.get(f"{self.base_url}/dislike/{self.user_id}")
        response.raise_for_status()
        self.dislikes = response.json()
        return response.json()

    def add_dislikes(self, dislike: str) -> dict:
        """
        Add a new dislike for the user.

        Creates a new dislike entry for the user via API call and
        refreshes the local dislikes list.

        Parameters
        ----------
        dislike : str
            The name of the dislike to add.

        Returns
        -------
        dict
            The response from the API containing the created dislike data.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(
            f"{self.base_url}/dislike/",
            json={"user_id": self.user_id, "dislike_name": dislike},
        )
        response.raise_for_status()
        self.dislikes = self.get_dislikes()
        return response.json()

    def delete_dislikes(self, dislike_id: int) -> dict:
        """
        Delete a user dislike by its ID.

        Removes a dislike from the user's profile via API call and
        refreshes the local dislikes list.

        Parameters
        ----------
        dislike_id : int
            The unique identifier of the dislike to delete.

        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.delete(
            f"{self.base_url}/dislike/{dislike_id}",
        )
        response.raise_for_status()
        self.dislikes = self.get_dislikes()
        return response.json()

    def get_allergies(self) -> list:
        """
        Get user allergies from the API.

        Retrieves all allergies associated with the user from the API
        and stores them in the instance's allergies attribute.

        Returns
        -------
        list
            A list of dictionaries containing allergy information.
            Each dictionary contains at least 'name' key.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """

        response = requests.get(f"{self.base_url}/user/{self.user_id}/allergies")
        response.raise_for_status()
        self.allergies = response.json()
        return response.json()

    def add_allergies(self, allergy: str) -> dict:
        """
        Add a new allergy for the user.

        Creates a new allergy entry for the user via API call and
        refreshes the local allergies list.

        Parameters
        ----------
        allergy : str
            The name of the allergy to add.

        Returns
        -------
        dict
            The response from the API containing the updated allergies list.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(
            f"{self.base_url}/user/{self.user_id}/allergies?allergy_name={allergy}"
        )
        response.raise_for_status()
        self.allergies = response.json()
        return response.json()

    def delete_allergies(self, allergy_name: str) -> dict:
        """
        Delete a user allergy by its name.

        Removes an allergy from the user's profile via API call and
        refreshes the local allergies list.

        Parameters
        ----------
        allergy_name : str
            The name of the allergy to delete.

        Returns
        -------
        dict
            The response from the API containing the updated allergies list.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.delete(
            f"{self.base_url}/user/{self.user_id}/allergies?allergy_name={allergy_name}"
        )
        response.raise_for_status()
        self.allergies = response.json()
        return response.json()


def get_all_users():
    """
    Get all user IDs.

    Returns
    -------
    list
        A list of user IDs.

    Notes
    -----
    This is a placeholder function that returns a fixed list.
    TODO: Add an API call rather than using a fixed list for an example.
    """
    return [1, 2, 3, 4, 5]


class OrderPurchase:
    """
    A class to manage order and purchase data for a user.

    Parameters
    ----------
    user_id : int
        The user's unique identifier.

    Attributes
    ----------
    user_id : int
        The user's unique identifier.
    base_url : str
        The base URL for API requests.
    open_order_and_purchases : list
        List of open (unchecked out) orders and purchases.
    closed_orders_and_purchases : list
        List of closed (checked out) orders and purchases.
    """

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.base_url = "http://api:8000"
        self.get_orders()

    def get_orders(self):
        """
        Fetch all orders and purchases for the user from the API.

        Separates orders into open (unchecked out) and closed (checked out) lists.
        Not every streamlit action will require a refresh of the orders from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.get(f"{self.base_url}/buy/{self.user_id}")
        response.raise_for_status()
        all_orders_and_purchases = response.json()
        self.open_order_and_purchases = [
            order
            for order in all_orders_and_purchases
            if order["order"]["checked_out"] is False
        ]
        self.closed_orders_and_purchases = [
            order
            for order in all_orders_and_purchases
            if order["order"]["checked_out"] is True
        ]

    def safe_open_order(self):
        """
        Get the single open order for the user.

        Returns
        -------
        dict or None
            The open order data if exactly one exists, None if no open orders.

        Raises
        ------
        ValueError
            If multiple open orders are found for the user.
        requests.RequestException
            If the API request fails during order fetching.
        """
        if not hasattr(self, "open_order_and_purchases"):
            self.get_orders()
        if len(self.open_order_and_purchases) > 1:
            raise ValueError(f"Multiple open orders found for user {self.user_id}")
        if len(self.open_order_and_purchases) == 0:
            return None
        return self.open_order_and_purchases[0]

    def consolidate_purchases_as_datafame(self, check_open_orders: bool):
        """
        Convert orders and purchases to a pandas DataFrame.

        Parameters
        ----------
        check_open_orders : bool
            If True, returns data for open orders. If False, returns data for
            closed orders.

        Returns
        -------
        pd.DataFrame
            A DataFrame with flattened order and purchase data.

        Raises
        ------
        requests.RequestException
            If the API request fails during order fetching.
        """
        if check_open_orders:
            if not hasattr(self, "open_order_and_purchases"):
                self.get_orders()
            orders = self.open_order_and_purchases
        else:
            if not hasattr(self, "closed_orders_and_purchases"):
                self.get_orders()
            orders = self.closed_orders_and_purchases
        flattened_data = []
        for order_data in orders:
            order_info = order_data["order"]
            purchases = order_data["purchases"]

            for purchase in purchases:
                row = {
                    "order_id": order_info["id"],
                    "order_total_amount": order_info["total_amount"],
                    "order_user_id": order_info["user_id"],
                    "order_created_at": order_info["created_at"],
                    "order_checked_out": order_info["checked_out"],
                    "order_updated_at": order_info["updated_at"],
                    "purchase_id": purchase["id"],
                    "quantity": purchase["quantity"],
                    "status": purchase["status"],
                    "product_id": purchase["product_id"],
                    "purchase_user_id": purchase["user_id"],
                    "purchase_total_amount": purchase["total_amount"],
                    "purchase_created_at": purchase["created_at"],
                    "purchase_updated_at": purchase["updated_at"],
                }
            flattened_data.append(row)
        return pd.DataFrame(flattened_data)

    def purchases_as_datafame(self, check_open_orders: bool):
        """
        Convert orders and purchases to a pandas DataFrame.

        Parameters
        ----------
        check_open_orders : bool
            If True, returns data for open orders. If False, returns data for
            closed orders.

        Returns
        -------
        pd.DataFrame
            A DataFrame with flattened order and purchase data.

        Raises
        ------
        requests.RequestException
            If the API request fails during order fetching.
        """
        if check_open_orders:
            if not hasattr(self, "open_order_and_purchases"):
                self.get_orders()
            orders = self.open_order_and_purchases
        else:
            if not hasattr(self, "closed_orders_and_purchases"):
                self.get_orders()
            orders = self.closed_orders_and_purchases
        flattened_data = []

        for order_data in orders:
            purchases = order_data["purchases"]

            for purchase in purchases:
                row = {
                    "purchase_id": purchase["id"],
                    "quantity": purchase["quantity"],
                    "status": purchase["status"],
                    "product_id": purchase["product_id"],
                    "purchase_user_id": purchase["user_id"],
                    "purchase_total_amount": purchase["total_amount"],
                    "purchase_created_at": purchase["created_at"],
                    "purchase_updated_at": purchase["updated_at"],
                }
                flattened_data.append(row)

        purchases_dataframe = pd.DataFrame(flattened_data)

        if not purchases_dataframe.empty:
            purchases_dataframe["purchase_created_at"] = pd.to_datetime(
                purchases_dataframe["purchase_created_at"], utc=True
            )
            purchases_dataframe["purchase_updated_at"] = pd.to_datetime(
                purchases_dataframe["purchase_updated_at"], utc=True
            )
            purchases_dataframe["quantity"] = pd.to_numeric(
                purchases_dataframe["quantity"], errors="coerce"
            )
            purchases_dataframe["purchase_total_amount"] = pd.to_numeric(
                purchases_dataframe["purchase_total_amount"], errors="coerce"
            )
            purchases_dataframe["purchase_id"] = pd.to_numeric(
                purchases_dataframe["purchase_id"], errors="coerce"
            )
            purchases_dataframe["product_id"] = purchases_dataframe[
                "product_id"
            ].astype(str)
            purchases_dataframe["purchase_user_id"] = pd.to_numeric(
                purchases_dataframe["purchase_user_id"], errors="coerce"
            )

        return purchases_dataframe

    def checkout(self):
        """
        Complete the checkout process for a user.


        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(f"{self.base_url}/buy/checkout/{self.user_id}")
        response.raise_for_status()
        return response.json()


def get_all_products():
    """
    Get all products from the API.

    Returns
    -------
    list
        A list of dictionaries containing product information.

    Raises
    ------
    requests.RequestException
        If the API request fails.
    """
    base_url = "http://api:8000"
    response = requests.get(f"{base_url}/product/")
    response.raise_for_status()
    return response.json()


def get_all_product_ids():
    """
    Get all product IDs from the API.

    Returns
    -------
    list
        A list of product IDs.

    Raises
    ------
    requests.RequestException
        If the API request fails.
    """
    response_json = get_all_products()
    return [product["id"] for product in response_json]


def get_all_active_in_stock_products():
    """
    Get all active products that are in stock.

    Returns
    -------
    list
        A list of dictionaries containing active, in-stock product information.

    Raises
    ------
    requests.RequestException
        If the API request fails.
    """
    response_json = get_all_products()
    return [
        product
        for product in response_json
        if product["is_active"] and product["quantity"] > 0
    ]

    

class Product:
    """
    A class to manage product data and operations.

    Parameters
    ----------
    product_id : str
        The product's unique identifier.

    Attributes
    ----------
    product_id : UUID
        The product's unique identifier.
    base_url : str
        The base URL for API requests.
    product_info : dict
        Dictionary containing product information from the API.
    """

    def __init__(self, product_id: str):
        self.product_id = UUID(product_id)
        self.base_url = "http://api:8000"
        self.get_product_info()

    def get_product_info(self):
        """
        Fetch product information from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.get(f"{self.base_url}/product/{self.product_id}")
        response.raise_for_status()
        self.product_info = response.json()

    def add_to_cart(self, product_id: str, user_id: int, quantity: int = 1):
        """
        Add a product to the user's cart.

        Parameters
        ----------
        product_id : str
            The product's unique identifier.
        user_id : int
            The user's unique identifier.
        quantity : int, optional
            The quantity to add to cart, by default 1.

        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        json_body = {"product_id": product_id, "user_id": user_id, "quantity": quantity}
        response = requests.post(f"{self.base_url}/buy", json=json_body)
        response.raise_for_status()
        return response.json()

    def increment_quanity(self, product_id: str, user_id: int, add: bool):
        """
        Increment or decrement the quantity of a product in the user's cart.

        Parameters
        ----------
        product_id : str
            The product's unique identifier.
        user_id : int
            The user's unique identifier.
        add : bool
            If True, increment quantity by 1. If False, decrement quantity by 1.

        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        if add:
            quantity = 1
        else:
            quantity = -1
        json_body = {"product_id": product_id, "user_id": user_id, "quantity": quantity}
        response = requests.put(f"{self.base_url}/buy", json=json_body)
        response.raise_for_status()
        return response.json()

