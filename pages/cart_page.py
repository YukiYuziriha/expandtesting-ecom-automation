# pages/cart_page.py
from playwright.sync_api import Page
from pages.base_page import BasePage
from urllib.parse import urljoin


class CartPage(BasePage):
    """Page Object for the ExpandTesting Bookstore Cart page."""

    URL = "/bookstore/cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.checkout_button = self.page.get_by_test_id("checkout")
        self.quantity_inputs = self.page.locator("input[name='cartQty']")
        self.update_buttons = self.page.locator("button[type='submit']")

    def load(self) -> None:
        self._safe_goto(self.URL)

    def is_cart_empty(self) -> bool:
        return self.page.locator("a[href^='/bookstore/remove/']").count() == 0

    def remove_item_by_index(self, index: int = 0) -> None:
        delete_link = self.page.locator("a[href^='/bookstore/remove/']").nth(index)

        href = delete_link.get_attribute("href")
        if href:
            # Correctly construct the full URL before navigating.
            full_url = urljoin(self.page.url, href)
            self.page.goto(full_url)

        self.page.wait_for_load_state("domcontentloaded")
        self.dismiss_any_ads()

    def proceed_to_checkout(self) -> None:
        self.checkout_button.click()
        self.page.wait_for_load_state("domcontentloaded")
