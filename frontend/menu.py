"""
Menu Configuration Module for Streamlit Navigation.

Defines menu structure and page configurations for the Streamlit application.
Manages role-based access control and provides functions that return Page
objects with relative file paths for dynamic navigation.

The menu system works by defining Page objects with relative paths to Python
files (e.g., "users/user_preferences.py") that are resolved relative to the current
working directory when st.navigation() loads them.

Key Functions:
- login(): Handles user authentication and role selection
- get_account_pages(): Returns account management pages (logout, settings)
- get_user_pages(): Returns buyer-accessible user pages
- get_admin_pages(): Returns admin-only management pages

File Path Resolution:
- Relative paths like "users/user_preferences.py" are resolved from the app's root
  directory
- st.navigation() automatically loads these files when pages are selected
- This allows for modular page organization without hardcoded absolute paths
"""

import streamlit as st
import user_and_requests

USER = [
    None,
    "john.smith@email.com",
    "sarah.johnson@email.com",
    "michael.williams@email.com",
    "emily.brown@email.com",
    "david.davis@email.com",
]
# These are the users in the example data
# TODO Add a route to get all users which would allow creating other users


def get_current_user_and_role():
    """
    Get the current user role from session state.
    Used to avoid resetting the role everytime the menu module is imported.

    Returns
    -------
    str or None
        The current user role
    """
    if "user" not in st.session_state:
        st.session_state.user = None
    if "role" not in st.session_state:
        st.session_state.role = None
    return st.session_state.user, st.session_state.role


def login():
    """
    Login page function that handles user authentication.

    Provides user selection interface where users choose access level. Updates
    session state with selected role and triggers page rerun to refresh
    navigation menu based on new role.

    Available roles:
    - None: Unauthenticated user (login page only)
    - Buyer: Can access user pages and account management.
    - Admin: Can access all pages including admin functions
    """
    st.header("Log In")
    user = st.selectbox("Select your user", USER)
    if st.button("Log In"):
        st.session_state.user = user_and_requests.User(email=user)
        if user == "david.davis@email.com":
            st.session_state.role = "Admin"
        else:
            st.session_state.role = "Buyer"
        st.rerun()


def get_account_pages():
    """
    Returns account management pages available to all authenticated users.

    Creates Page objects for account-related functions:
    - Logout: Clears session state and returns to login
    - Settings: Links to settings.py file for user preferences

    Returns
    -------
    list
        List of st.Page objects for account management
    """

    def logout():
        st.session_state.user = None
        st.session_state.role = None
        st.rerun()

    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
    account_pages = [logout_page, settings]
    return account_pages


def get_user_pages():
    """
    Returns user pages available to Buyer and Admin users.

    Creates Page objects with relative file paths to user modules:
    - user_preferences.py: User preferences interface (default for Buyer user)
    - sales_page.py: Sales page interface

    The relative paths (e.g., "users/user_preferences.py") are resolved by
    st.navigation() when the pages are loaded.

    Returns
    -------
    list
        List of st.Page objects for user functionality
    """
    user, role = get_current_user_and_role()
    user_preferences = st.Page(
        "users/user_preferences.py",
        title="My Interests",
        icon=":material/help:",
        default=(role == "Buyer"),
    )
    sales_page = st.Page(
        "users/sales_page.py", title="Sales Page", icon=":material/shopping_cart:"
    )

    user_pages = [user_preferences, sales_page]
    return user_pages


def get_admin_pages():
    """
    Returns admin pages available only to Admin user.

    Creates Page objects with relative file paths to admin modules:
    - sales_metrics.py: Sales metrics dashboard (default for Admin user)
    - admin_2.py: Secondary admin interface

    The relative paths (e.g., "admin/sales_metrics.py") are resolved by
    st.navigation() when the pages are loaded.

    Returns
    -------
    list
        List of st.Page objects for admin functionality
    """
    user, role = get_current_user_and_role()
    sales_metrics = st.Page(
        "admin/sales_metrics.py",
        title="Sales Metrics",
        icon=":material/analytics:",
        default=(role == "Admin"),
    )
    # admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")
    admin_pages = [sales_metrics]
    return admin_pages
