"""
Streamlit Application Main Entry Point.

Orchestrates app structure, authentication, sidebar config, and dynamic page
navigation based on user roles. Uses menu-driven navigation where menu.py
defines page configurations with relative file paths that st.navigation()
dynamically loads.

Key Components:
- Role-based access control (Buyer, Admin, None)
- Dynamic page loading from relative paths
- Sidebar branding with logo and description
- Session state management for user authentication
"""

import streamlit as st
import menu


def run_app():
    """
    Main application runner that sets up the Streamlit interface.

    Configures title, sidebar branding, role-based access control, and dynamic
    navigation menus. The navigation system works by menu.py returning Page
    objects with relative file paths (e.g., "request/request_1.py") that
    st.navigation() automatically loads when pages are selected.
    """
    st.title("My App")

    # st.sidebar always renders at the bottom of the sidebar
    st.sidebar.image("images/mockbasket.png")
    st.sidebar.title("Mock Basket")
    st.sidebar.write("Your favorite example website!")
    st.sidebar.link_button(
        "GitHub Repo",
        "https://github.com/mgolesberg/api-example",
        type="primary",
        help="Link to Repo and Docs",
        use_container_width=False,
    )

    page_dict = {}
    user, role = menu.get_current_user_and_role()

    if role in ["Buyer", "Admin"]:
        page_dict["Buyer"] = menu.get_request_pages()
    if role == "Admin":
        page_dict["Admin"] = menu.get_admin_pages()

    if len(page_dict) > 0:  # Marks when the user is logged in
        pg = st.navigation({"Account": menu.get_account_pages()} | page_dict)
    else:
        pg = st.navigation([st.Page(menu.login)])

    pg.run()


def main():
    """
    Entry point function that calls the main application runner.

    Ensures the app can be run both as a module and as a script.
    """
    run_app()


if __name__ == "__main__":
    main()
