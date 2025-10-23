# tests/smoke/test_base_page.py
import pytest
from bookstore.pages.base_page import BasePage


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
def test_logout(logged_in_page: BasePage) -> None:
    assert logged_in_page.is_logged_in()
    logged_in_page.logout()
    assert not logged_in_page.is_logged_in()
