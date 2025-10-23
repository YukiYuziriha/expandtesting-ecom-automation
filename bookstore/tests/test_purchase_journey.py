# bookstore/tests/test_purchase_journey.py
import pytest
from bookstore.pages.home_page import HomePage
from bookstore.pages.cart_page import CartPage
from bookstore.pages.checkout_page import CheckoutPage
from bookstore.pages.profile_page import ProfilePage
from playwright.sync_api import expect


@pytest.mark.bookstore
@pytest.mark.ui
@pytest.mark.e2e
def test_authenticated_purchase_journey(
    logged_in_page, test_users, profile_name: str
) -> None:
    """
    P0 E2E Full authenticated purchase flow.
    Covers: search, add to cart, checkout, order confirmation.
    """
    page = logged_in_page.page

    # Step 1: Go to home and search
    home_page = HomePage(page)
    home_page.load()
    home_page.search_for("Dev")
    home_page.wait_for_search_results()

    # Step 2: Add first book to cart and wait for badge update
    home_page.add_book_to_cart_by_index(0)

    expect(home_page.cart_badge).to_have_text("1")

    # Step 3: Go to cart and proceed to checkout
    cart_page = CartPage(page)
    cart_page.load()
    cart_page.proceed_to_checkout()
    page.wait_for_url("**/checkout")

    # Step 4: Fill and submit checkout form
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

    profile_page = ProfilePage(page)

    expect(profile_page.order_confirmation_banner).to_be_visible(timeout=10000)
