# pages/base_page.py
from playwright.sync_api import Page, TimeoutError


class BasePage:
    """Base page with shared UI elements (e.g., navbar, logout)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.user_dropdown_toggle = page.locator("#navbarDropdown")
        self.logout_link = page.locator("#logout")
        self.cart_badge = page.locator("a[href='/bookstore/cart']")

    def _safe_goto(self, url: str) -> None:
        """Navigate and auto-dismiss ads."""
        self.page.goto(url)
        self.dismiss_any_ads()

    def dismiss_any_ads(self) -> None:
        """
        Attempt to dismiss interstitial ads ONLY if they appear as DOM overlays
        (not inside iframes). This avoids accidental ad clicks.
        """
        try:
            # Look for ad container in MAIN page DOM (not inside iframes)
            ad_container = self.page.locator("#card:has(.creative)")
            if ad_container.is_visible(timeout=500):
                # Try to find close button in main document
                close_btn = self.page.get_by_label("Close ad").or_(
                    self.page.locator("#dismiss-button")
                )
                if close_btn.is_visible(timeout=500):
                    close_btn.click(timeout=1000)
                    ad_container.wait_for(state="hidden", timeout=2000)
        except TimeoutError:
            pass

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
