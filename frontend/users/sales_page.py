"""
Sales Page Module.

This module provides the main product browsing and purchasing interface for users
in the Streamlit application. It displays all active, in-stock products with
detailed information and allows users to add items to their cart.

Key Features:
- Product catalog display with images and descriptions
- Detailed product information including pricing
- Add to cart functionality
- Responsive layout with image and text columns
- Styled product cards with modern UI elements

The sales page serves as the primary shopping interface, allowing both Buyer and
Admin users to browse products and make purchases. It integrates with the Product
class from user_and_requests to fetch product data and handle cart operations.

Product Display:
- Shows product images, names, descriptions, and prices
- Uses styled HTML for enhanced visual presentation
- Provides clear call-to-action buttons for adding to cart
- Displays success messages when items are added

Usage:
    This module is automatically loaded by the Streamlit navigation system
    when users select the Sales Page from the Buyer menu. The main function
    display_all_products() renders the complete product catalog.
"""

import streamlit as st
import user_and_requests


def product_details(product_id: str):
    """
    Display detailed product information in a Streamlit interface.

    Parameters
    ----------
    product_id : str
        The unique identifier of the product to display.
    """
    st.markdown("----")
    product = user_and_requests.Product(product_id)
    image_column, text_column = st.columns([0.4, 0.6])
    with image_column:
        st.subheader("")  # This is just to match the height
        st.image(product.product_info["image_url"])
    with text_column:
        st.subheader(product.product_info["name"])
        st.markdown(
            f"""
        <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px; 
                    border-left: 4px solid #667eea; margin: 15px 0;">
            <p style="font-size: 1.1em; line-height: 1.6; color: #495057; margin: 0;">
                {product.product_info['description']}
            </p>
        </div>
        """,
            unsafe_allow_html=True,
        )
        price = product.product_info["price"]
        st.markdown(
            f"""
        <div style="background-color: #ffffff; padding: 12px 20px; border-radius: 8px; 
                    border: 2px solid #e9ecef; margin: 10px 0; text-align: center;">
            <span style="font-size: 1.4em; font-weight: 600; color: #495057;">
                ${price}
            </span>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("Add to Cart", key=f"add_to_cart_{product_id}"):
            product.add_to_cart(product_id, st.session_state.user.user_id)
            st.success(f"{product.product_info['name']} added to cart!")


def display_all_products():
    """
    Display all active, in-stock products in the Streamlit interface.

    Raises
    ------
    requests.RequestException
        If the API request fails.
    """
    for product in user_and_requests.get_all_active_in_stock_products():
        product_details(product["id"])


if __name__ == "__main__":
    display_all_products()
