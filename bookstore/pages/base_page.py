# pages/base_page.py
from playwright.sync_api import Page
from config import BASE_URL


class BasePage:
    """Base page with shared UI elements (e.g., navbar, logout)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.user_dropdown_toggle = page.locator("#navbarDropdown")
        self.logout_link = page.locator("#logout")
        self.cart_badge = page.locator("a[href='/bookstore/cart']")

    def _safe_goto(self, url: str) -> None:
        """Navigate to a URL relative to BASE_URL."""
        full_url = f"{BASE_URL}{url}"
        self.page.goto(full_url, wait_until="domcontentloaded")

    def is_logged_in(self) -> bool:
        """
        Returns True if user dropdown is present (logged in), False otherwise.
        """
        return self.user_dropdown_toggle.is_visible(timeout=1000)

    def logout(self) -> None:
        """Log out the current user via the global navbar."""
        self.user_dropdown_toggle.click()
        self.logout_link.click()

    def read_cart_count(self) -> int:
        """Returns the numeric value in the cart badge (0 if empty)."""
        text = self.cart_badge.text_content()
        if text is None:
            return 0
        clean_text = text.strip()
        return int(clean_text) if text and clean_text.isdigit() else 0
