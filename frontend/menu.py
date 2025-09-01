"""
Menu Configuration Module for Streamlit Navigation.

Defines menu structure and page configurations for the Streamlit application.
Manages role-based access control and provides functions that return Page
objects with relative file paths for dynamic navigation.

The menu system works by defining Page objects with relative paths to Python
files (e.g., "request/request_1.py") that are resolved relative to the current
working directory when st.navigation() loads them.

Key Functions:
- login(): Handles user authentication and role selection
- get_account_pages(): Returns account management pages (logout, settings)
- get_request_pages(): Returns buyer-accessible request pages
- get_admin_pages(): Returns admin-only management pages

File Path Resolution:
- Relative paths like "request/request_1.py" are resolved from the app's root
  directory
- st.navigation() automatically loads these files when pages are selected
- This allows for modular page organization without hardcoded absolute paths
"""

import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Buyer", "Admin"]
role = st.session_state.role


def login():
    """
    Login page function that handles user authentication.

    Provides role selection interface where users choose access level. Updates
    session state with selected role and triggers page rerun to refresh
    navigation menu based on new role.

    Available roles:
    - None: Unauthenticated user (login page only)
    - Buyer: Can access request pages and account management
    - Admin: Can access all pages including admin functions
    """
    st.header("Log In")
    role = st.selectbox("Select your role", ROLES)
    if st.button("Log In"):
        st.session_state.role = role
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
        st.session_state.role = None
        st.rerun()

    logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
    settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
    account_pages = [logout_page, settings]
    return account_pages


def get_request_pages():
    """
    Returns request pages available to Buyer and Admin roles.

    Creates Page objects with relative file paths to request modules:
    - request_1.py: Primary request interface (default for Buyer role)
    - request_2.py: Secondary request interface

    The relative paths (e.g., "request/request_1.py") are resolved by
    st.navigation() when the pages are loaded.

    Returns
    -------
    list
        List of st.Page objects for request functionality
    """
    request_1 = st.Page(
        "request/request_1.py",
        title="Request 1",
        icon=":material/help:",
        default=(role == "Buyer"),
    )
    request_2 = st.Page(
        "request/request_2.py", title="Request 2", icon=":material/bug_report:"
    )

    request_pages = [request_1, request_2]
    return request_pages


def get_admin_pages():
    """
    Returns admin pages available only to Admin role.

    Creates Page objects with relative file paths to admin modules:
    - admin_1.py: Primary admin interface (default for Admin role)
    - admin_2.py: Secondary admin interface

    The relative paths (e.g., "admin/admin_1.py") are resolved by
    st.navigation() when the pages are loaded.

    Returns
    -------
    list
        List of st.Page objects for admin functionality
    """
    admin_1 = st.Page(
        "admin/admin_1.py",
        title="Admin 1",
        icon=":material/person_add:",
        default=(role == "Admin"),
    )
    admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")
    admin_pages = [admin_1, admin_2]
    return admin_pages
