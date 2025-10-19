# pages/login_page.py
from playwright.sync_api import Page
from bookstore.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the ExpandTesting Bookstore Sign-In page."""

    URL = "/bookstore/user/signin"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        login_form = (
            self.page.locator("form")
            .filter(has=self.page.locator("#email"))
            .filter(has=self.page.locator("#password"))
        )
        self.email_input = login_form.locator("#email")
        self.password_input = login_form.locator("#password")
        self.sign_in_button = login_form.locator("button[type='submit']")

    def load(self) -> None:
        """Navigate to the login page."""
        self._safe_goto(self.URL)

    def login(self, email: str, password: str) -> None:
        """Perform login action with given credentials."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()

    @property
    def credentials_error_message(self):
        """
        Locator for the universal error banner (id='flash')
        Use expect(...).to_be_visible() to check if any error is shown.
        Use .text_content() or inner_text() to read the message.
        """
        return self.page.locator("#flash.alert.alert-danger")
