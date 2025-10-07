# pages/login_page.py
from playwright.sync_api import Page


class LoginPage:
    """Page Object for the ExpandTesting Bookstore Sign-In page."""

    URL = "https://practice.expandtesting.com/bookstore/user/signin"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.email_input = page.get_by_placeholder("Enter your email...")
        self.password_input = page.get_by_placeholder("Enter your password...")
        self.sign_in_button = page.get_by_role("button", name="Sign In")

    def load(self) -> None:
        """Navigate to the login page."""
        self.page.goto(self.URL)

    def login(self, email: str, password: str) -> None:
        """Perform login action with given credentials."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()

    @property
    def missing_credentials_error(self):
        return self.page.get_by_text("Missing credentials")

    @property
    def invalid_email_error(self):
        return self.page.get_by_text("Invalid email address")
