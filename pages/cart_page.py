# pages/cart_page.py
from playwright.sync_api import Page, expect
from pages.base_page import BasePage


class CartPage(BasePage):
    """Page Object for the ExpandTesting Bookstore Cart page."""

    URL = "https://practice.expandtesting.com/bookstore/cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.checkout_button = self.page.get_by_test_id("checkout")
        self.quantity_inputs = self.page.locator("input[name='cartQty']")
        self.update_buttons = self.page.locator("button[type='submit']")
        self.cart_items = self.page.locator("a[href^='/bookstore/remove/']")

    def load(self) -> None:
        self._safe_goto(self.URL)

    def is_cart_empty(self) -> bool:
        """Check if cart is empty with proper waiting."""
        self.page.wait_for_timeout(1000)
        return self.cart_items.count() == 0

    def remove_item_by_index(self, index: int = 0) -> None:
        """Remove item with proper waiting and verification."""
        initial_count = self.cart_items.count()
        if initial_count == 0:
            return

        delete_link = self.cart_items.nth(index)
        delete_link.click()

        # Wait for cart to update
        expect(self.cart_items).to_have_count(initial_count - 1, timeout=5000)

    def proceed_to_checkout(self) -> None:
        """Proceed to checkout with verification."""
        self.checkout_button.click()
        self.page.wait_for_url("**/checkout", timeout=10000)
