# tests/ test_purchase_journey.py
from pages.home_page import HomePage
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.profile_page import ProfilePage


def test_authenticated_purchase_journey(logged_in_page, test_users) -> None:
    """
    P0 E2E Full authenticated purchase flow.
    Covers: search, add to cart, checkout, order confirmation.
    """
    page = logged_in_page.page

    # Step 1: Go to home and search
    home_page = HomePage(page)
    home_page.load()
    home_page.search_for("Dev")

    # Step 2: Add first book to cart
    home_page.add_book_to_cart_by_index(0)
    page.wait_for_load_state("domcontentloaded")

    # Step 3: Go to cart and proceed to checkout
    cart_page = CartPage(page)
    cart_page.load()
    cart_page.proceed_to_checkout()

    # Step 4: Fill and submit chechout form
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
    assert (
        profile_page.is_order_confirmation_visible()
    ), "Order confirmation banner not shown"
