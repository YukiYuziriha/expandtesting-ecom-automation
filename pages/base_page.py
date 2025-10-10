# pages/base_page.py
from playwright.sync_api import Page


class BasePage:
    """Base page with shared UI elements (e.g., navbar, logout)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.user_dropdown_toggle = page.locator("#navbarDropdown")
        self.logout_link = page.locator("#logout")

    def logout(self) -> None:
        """Log out the current user via the global navbar."""
        self.user_dropdown_toggle.click()
        self.logout_link.click()
