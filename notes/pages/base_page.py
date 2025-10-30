# notes/pages/base_page.py
from playwright.sync_api import Page
from config import BASE_URL


class BasePage:
    """Base page with shared UI elements (e.g., navbar, logout)."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def goto(self, path: str) -> None:
        self.page.goto(f"{BASE_URL}{path}")
