import streamlit as st

if "role" not in st.session_state:
    st.session_state.role = None

ROLES = [None, "Buyer", "Admin"]


def login():
    st.header("Log In")
    role = st.selectbox("Select your role", ROLES)
    if st.button("Log In"):
        st.session_state.role = role
        st.rerun()


def logout():
    st.session_state.role = None
    st.rerun()


role = st.session_state.role

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
settings = st.Page("settings.py", title="Settings", icon=":material/settings:")
request_1 = st.Page(
    "request/request_1.py",
    title="Request 1",
    icon=":material/help:",
    default=(role == "Buyer"),
)
request_2 = st.Page(
    "request/request_2.py", title="Request 2", icon=":material/bug_report:"
)

admin_1 = st.Page(
    "admin/admin_1.py",
    title="Admin 1",
    icon=":material/person_add:",
    default=(role == "Admin"),
)
admin_2 = st.Page("admin/admin_2.py", title="Admin 2", icon=":material/security:")

account_pages = [logout_page, settings]
request_pages = [request_1, request_2]
admin_pages = [admin_1, admin_2]

st.title("My App")

st.logo("mockbasket.png", size="large")

page_dict = {}

if st.session_state.role in ["Buyer", "Admin"]:
    page_dict["Buyer"] = request_pages
if st.session_state.role == "Admin":
    page_dict["Admin"] = admin_pages

if len(page_dict) > 0:  # Marks when the user is logged in
    pg = st.navigation({"Account": account_pages} | page_dict)
else:
    pg = st.navigation([st.Page(login)])

pg.run()
