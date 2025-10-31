from playwright.sync_api import Page
from notes.pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for the ExpandTesting Notes Home page."""

    URL = "/notes/app"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

    def load(self) -> None:
        self.goto(self.URL)
