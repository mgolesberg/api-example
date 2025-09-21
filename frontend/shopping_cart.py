"""
Shopping Cart Module for Streamlit Frontend.

This module provides functionality for displaying and managing shopping cart items
in the Streamlit frontend application. It integrates with the user_and_requests
module to interact with the FastAPI backend for cart operations.

Functions
---------
get_cart_items()
    Retrieve cart items for the current user from the API.
display_a_cart_item(product_row)
    Display a single cart item with product details and quantity controls.
display_cart_items()
    Display all cart items with total calculation.

Notes
-----
This module requires a user session state to be established before use.
It uses the OrderPurchase and Product classes from user_and_requests module
to fetch cart data and manage product operations.

The module provides interactive controls for incrementing/decrementing
product quantities and displays real-time cart totals.


"""

import streamlit as st
import user_and_requests
import pandas as pd

st.header("Shopping Cart")


def get_cart_items():
    """
    Retrieve cart items for the current user from the API.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing cart items with purchase details.
        Returns empty DataFrame if no open order exists.

    Raises
    ------
    requests.RequestException
        If the API request fails.
    ValueError
        If multiple open orders are found for the user.
    """
    orders = user_and_requests.OrderPurchase(st.session_state.user.user_id)
    open_order = orders.safe_open_order()
    if open_order:
        orders_dataframe = orders.purchases_as_datafame(True)
        return orders_dataframe
    else:
        return pd.DataFrame()


def display_a_cart_item(product_row):
    """
    Display a single cart item with product details and quantity controls.

    Parameters
    ----------
    product_row : pd.Series
        A pandas Series containing product purchase data including
        product_id, purchase_total_amount, quantity, and purchase_id.

    Raises
    ------
    requests.RequestException
        If the API request fails when fetching product information.
    """
    product = user_and_requests.Product(product_row["product_id"])
    image_column, text_column = st.columns([0.3, 0.7])
    with image_column:
        st.subheader("")  # This is just to match the height
        st.image(product.product_info["image_url"])
    with text_column:
        st.subheader(product.product_info["name"])
        st.markdown(
            f"""
        <div style="background-color: #ffffff; padding: 12px 20px; border-radius: 8px;
                    border: 2px solid #e9ecef; margin: 10px 0; text-align: center;">
            <span style="font-size: 1.4em; font-weight: 600; color: #495057;">
                ${product_row["purchase_total_amount"]}
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;
                    border-left: 4px solid #667eea; margin: 15px 0;
                    text-align: center;">
            <p style="font-size: 1.4em; font-weight: 600; line-height: 1.6;
               color: #495057; margin: 0;">
                Qty: {product_row["quantity"]}
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        _, decrease_button, increase_button, _ = st.columns(4)
        with decrease_button:
            if st.button("➖", key=f"decrease_{product_row['purchase_id']}"):
                product.increment_quanity(
                    product_row["product_id"], st.session_state.user.user_id, False
                )
                st.rerun()
        with increase_button:
            if st.button("➕", key=f"increase_{product_row['purchase_id']}"):
                product.increment_quanity(
                    product_row["product_id"], st.session_state.user.user_id, True
                )
                st.rerun()


def display_cart_items():
    """
    Display all cart items with total calculation.

    This function retrieves all cart items for the current user and displays
    them with interactive quantity controls. It calculates and displays the
    total amount for all items with "In cart" status.

    Raises
    ------
    requests.RequestException
        If the API request fails when fetching cart data.
    ValueError
        If multiple open orders are found for the user.
    """
    active_amount = 0
    products_dataframe = get_cart_items()
    for _, row in products_dataframe.iterrows():
        if row["status"] == "In cart":
            display_a_cart_item(row)
            active_amount += row["purchase_total_amount"]
    st.markdown(
        f"""
        <div style="background-color: #ffffff; padding: 12px 20px; border-radius: 8px;
                    border: 2px solid #e9ecef; margin: 10px 0; text-align: center;">
            <span style="font-size: 1.4em; font-weight: 600; color: #495057;">
                Current total: ${active_amount:.2f}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    display_cart_items()
