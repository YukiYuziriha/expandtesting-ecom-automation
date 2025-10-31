# tests/smoke/test_checkout_page.py
import re
import pytest
from bookstore.pages.home_page import HomePage
from bookstore.pages.cart_page import CartPage
from bookstore.pages.checkout_page import CheckoutPage
from bookstore.pages.profile_page import ProfilePage
from bookstore.pages.base_page import BasePage
from playwright.sync_api import expect


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.smoke
@pytest.mark.e2e
def test_checkout_smoke(
    logged_in_page: BasePage, test_users: dict, profile_name: str, orders_cleanup
) -> None:
    """
    Smoke test for the full authenticated purchase journey.
    """
    page = logged_in_page.page

    home_page = HomePage(page)
    home_page.load()
    home_page.add_book_to_cart_by_index(0)
    expect(home_page.cart_badge).to_have_text("1")

    cart_page = CartPage(page)
    cart_page.load()
    cart_page.proceed_to_checkout()

    user = test_users[profile_name]
    checkout_page = CheckoutPage(page)

    checkout_page.fill_and_submit(
        name=user["billing"]["name"],
        address=user["billing"]["address"],
        card_name="Test Cardholder",
        card_number=user["payment"]["card_number"],
        exp_month=user["payment"]["exp_month"],
        exp_year=user["payment"]["exp_year"],
        cvc=user["payment"]["cvc"],
    )

    # Wait for navigation to profile page
    expect(page).to_have_url(re.compile(r".*/profile"), timeout=10_000)

    profile_page = ProfilePage(page)
    expect(profile_page.order_confirmation_banner).to_be_visible(timeout=15000)
