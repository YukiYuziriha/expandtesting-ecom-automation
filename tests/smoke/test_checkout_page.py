# tests/smoke/test_checkout_page.py
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.profile_page import ProfilePage
from pages.base_page import BasePage


def test_checkout_smoke(logged_in_page: BasePage, test_users: dict) -> None:
    """
    Smoke test for the full authenticated purchase journey.
    """
    page = logged_in_page.page

    home_page = HomePage(page)
    home_page.load()
    home_page.add_book_to_cart_by_index(0)
    page.wait_for_load_state("domcontentloaded")
    assert home_page.read_cart_count() == 1

    cart_page = CartPage(page)
    cart_page.load()
    cart_page.proceed_to_checkout()

    user = test_users["profile1"]
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

    page.wait_for_url("**/profile")

    profile_page = ProfilePage(page)
    assert profile_page.is_order_confirmation_visible()
