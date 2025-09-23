from unittest.mock import MagicMock, patch
from frontend import streamlit_app


@patch("frontend.streamlit_app.run_app")
def test_run_app(mock_run_app):

    streamlit_app.main()
    mock_run_app.assert_called_once()


@patch("streamlit_app.menu")
@patch("streamlit.title")
@patch("streamlit.sidebar")
def test_run_app_streamlit_components(mock_sidebar, mock_title, mock_menu):
    mock_menu.get_current_user_and_role.return_value = (MagicMock(), MagicMock())

    streamlit_app.run_app()

    mock_title.assert_called_once_with("My App")
    mock_sidebar.image.assert_called_once_with("images/mockbasket.png")
    mock_sidebar.title.assert_called_once_with("Mock Basket")
    mock_sidebar.write.assert_called_once_with("Your favorite example website!")


@patch("menu.get_current_user_and_role")
@patch("menu.get_user_pages")
@patch("menu.get_admin_pages")
@patch("menu.get_account_pages")
@patch("streamlit.title")
@patch("streamlit.sidebar")
def test_run_app_with_menu(
    mock_sidebar,
    mock_title,
    mock_get_account_pages,
    mock_get_admin_pages,
    mock_get_user_pages,
    mock_get_current_user_and_role,
):
    mock_get_current_user_and_role.return_value = ("user", "Admin")
    mock_get_user_pages.return_value = ["page1", "page2"]
    mock_get_admin_pages.return_value = ["page3", "page4"]
    mock_get_account_pages.return_value = ["page5", "page6"]

    streamlit_app.run_app()

    mock_get_current_user_and_role.assert_called_once()
    mock_get_user_pages.assert_called_once()
    mock_get_admin_pages.assert_called_once()
    mock_get_account_pages.assert_called_once()
