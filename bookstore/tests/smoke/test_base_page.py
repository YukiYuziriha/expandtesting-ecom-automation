# tests/smoke/test_base_page.py
from bookstore.pages.base_page import BasePage


def test_logout(logged_in_page: BasePage) -> None:
    assert logged_in_page.is_logged_in()
    logged_in_page.logout()
    assert not logged_in_page.is_logged_in()
