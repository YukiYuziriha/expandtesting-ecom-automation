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
        Finds the correct ad iframe from multiple candidates and clicks its close button.
        """
        # Get all potential ad iframes on the page.
        ad_iframes = self.page.locator("iframe[title='Advertisement']").all()

        for frame_locator in ad_iframes:
            try:
                # For each frame, try to find and click the close button inside it.
                # Use a very short timeout because we only care about the one that is currently visible.
                close_button = (
                    frame_locator.frame_locator(":scope")
                    .get_by_label("Close ad")
                    .or_(
                        frame_locator.frame_locator(":scope").locator("#dismiss-button")
                    )
                )
                close_button.click(timeout=250)

                # If the click was successful, the ad is closed, and we can stop looking.
                return
            except (TimeoutError, Exception):
                # If this frame didn't contain the visible close button, ignore the error and try the next one.
                continue

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
