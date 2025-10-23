# tests/smoke/test_cart_page.py
import pytest
from playwright.sync_api import Page
from bookstore.pages.cart_page import CartPage
from bookstore.pages.home_page import HomePage


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
def test_cart_is_empty(page: Page) -> None:
    cart_page = CartPage(page)
    cart_page.load()

    assert cart_page.is_cart_empty()


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
def test_can_remove_cart_item(page: Page) -> None:
    home_page = HomePage(page)
    home_page.load()
    home_page.add_book_to_cart_by_index(0)

    cart_page = CartPage(page)
    cart_page.load()
    cart_page.remove_item_by_index(index=0)

    assert cart_page.is_cart_empty()
