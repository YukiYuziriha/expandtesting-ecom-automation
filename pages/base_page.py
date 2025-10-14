# pages/base_page.py
from playwright.sync_api import Page


class BasePage:
    """Base page with shared UI elements and robust ad handling."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.user_dropdown_toggle = page.locator("#navbarDropdown")
        self.logout_link = page.locator("#logout")
        self.cart_badge = page.locator("a[href='/bookstore/cart']")

    def _safe_goto(self, url: str) -> None:
        """Navigate with ad blocking and proper waiting."""
        # Block ads before navigation
        self._block_ads()
        self.page.goto(url)
        self.page.wait_for_load_state("networkidle")
        self.dismiss_any_ads()

    def _block_ads(self) -> None:
        """Block common ad domains at network level."""
        ad_patterns = [
            "*googleads*",
            "*googlesyndication*",
            "*doubleclick*",
            "*adsbygoogle*",
        ]

        def block_route(route):
            if any(pattern in route.request.url for pattern in ad_patterns):
                route.abort()
            else:
                route.continue_()

        self.page.route("**/*", block_route)

    def dismiss_any_ads(self) -> None:
        """Robust ad dismissal with multiple strategies."""
        try:
            # Strategy 1: Close buttons
            close_selectors = [
                "button[aria-label*='close' i]",
                "button[class*='close' i]",
                "#dismiss-button",
                "[data-testid*='close']",
            ]

            for selector in close_selectors:
                if self.page.locator(selector).is_visible(timeout=1000):
                    self.page.locator(selector).click()
                    self.page.wait_for_timeout(500)  # Brief pause
                    break

            # Strategy 2: Hide ad containers via JS
            hide_script = """
                document.querySelectorAll('ins.adsbygoogle, .adsbygoogle, [class*="ad-"]')
                    .forEach(el => el.style.display = 'none');
            """
            self.page.evaluate(hide_script)

        except Exception:
            # Silently continue if no ads found
            pass

    def is_logged_in(self) -> bool:
        """Check if user is logged in with proper waiting."""
        return self.user_dropdown_toggle.is_visible(timeout=5000)

    def logout(self) -> None:
        """Log out with proper waiting."""
        self.user_dropdown_toggle.click()
        self.logout_link.click()
        self.page.wait_for_load_state("networkidle")

    def read_cart_count(self) -> int:
        """Safely read cart count with error handling."""
        try:
            text = self.cart_badge.text_content(timeout=2000)
            return int(text.strip()) if text and text.strip().isdigit() else 0
        except Exception:
            return 0

    def wait_for_element(self, locator, timeout=10000):
        """Wait for element to be visible and stable."""
        element = self.page.locator(locator)
        element.wait_for(state="visible", timeout=timeout)
        return element
