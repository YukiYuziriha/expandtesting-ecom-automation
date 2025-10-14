# pages/home_page.py
from playwright.sync_api import Page
from pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for the ExpandTesting Bookstore Home page."""

    URL = "https://practice.expandtesting.com/bookstore"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # Search bar capture
        search_form = self.page.locator("form").filter(
            has=self.page.locator("button[type='submit']")
        )
        self.search_input = search_form.get_by_role("textbox")
        self.search_button = search_form.locator("button[type='submit']")

        self.add_to_cart_buttons = self.page.locator("[data-testid^='cart-']")

    def load(self) -> None:
        self._safe_goto(self.URL)

    def search_for(self, query: str) -> None:
        self.search_input.fill(query)
        self.search_button.click()
        self.wait_for_search_results()

    def add_book_to_cart_by_index(self, index: int = 0) -> None:
        target_button = self.add_to_cart_buttons.nth(index)
        # Wait for button to be actionable (visible + stable)
        target_button.wait_for(state="attached", timeout=3000)
        target_button.click()

    @property
    def book_titles(self):
        """Locator for all book title elements (data-testid starts with 'title-')."""
        return self.page.locator("[data-testid^='title-']")

    def wait_for_search_results(self) -> None:
        """Wait until at least `min_count` book titles are visible."""
        self.book_titles.first.wait_for(state="visible")
