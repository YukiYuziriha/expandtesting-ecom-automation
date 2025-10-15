# pages/profile_page.py
from playwright.sync_api import Page
from pages.base_page import BasePage


class ProfilePage(BasePage):
    """Page Object for the user Profile page with order history."""

    URL = "https://practice.expandtesting.com/bookstore/user/profile"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.order_confirmation_banner = self.page.locator("#flash.alert.alert-success")

    def load(self) -> None:
        """Navigate to the profile page."""
        self._safe_goto(self.URL)

    def is_order_confirmation_visible(self) -> bool:
        """Check if the order confirmation banner is visible."""
        return self.order_confirmation_banner.is_visible(timeout=5000)
