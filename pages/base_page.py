# pages/base_page.py
from playwright.sync_api import Page


class BasePage:
    """Base page with shared UI elements (e.g., navbar, logout)."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.user_dropdown_toggle = page.locator("#navbarDropdown")
        self.logout_link = page.locator("#logout")

    def dismiss_any_ads(self, timeout: float = 2000) -> None:
        """
        Attempt to dismiss intersitial ads if present.
        Runs quickly and silently if no ad is found.
        """
        try:
            ad_container = self.page.locator("#card:has(.creative)")
            if not ad_container.is_visible(timeout=500):
                return

            close_button = ad_container.get_by_role("button", name="Close ad").or_(
                ad_container.locator("#dismiss-button")
            )
            if close_button.is_visible(timeout=500):
                close_button.click(timeout=500)
                ad_container.wait_for(state="hidden", timeout=2000)
        except TimeoutError:
            pass

    def logout(self) -> None:
        """Log out the current user via the global navbar."""
        self.user_dropdown_toggle.click()
        self.logout_link.click()
