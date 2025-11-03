from playwright.sync_api import Page, Locator
from notes.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for the ExpandTesting Notes Sign-In page."""

    URL = "/notes/app/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.email_input = page.get_by_test_id("login-email")
        self.password_input = page.get_by_test_id("login-password")
        self.login_button = page.get_by_test_id("login-submit")

    def load(self) -> None:
        self.goto(self.URL)

    def login(self, email: str, password: str) -> None:
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_button.click()

    @property
    def credentials_error_message(self):
        """
        Locator for the error banner "Incorrect email address or password".
        Use expect(...).to_be_visible() to check if any error is shown.
        Use .text_content() or inner_text() to read the message.
        """
        return self.page.get_by_test_id("alert-message")

    @property
    def logged_in_marker(self) -> Locator:
        """Locator that indicates successful login."""
        return self.page.get_by_test_id("notes-list")

    @property
    def logged_out_marker(self) -> Locator:
        """
        Locator that indicates logged out state.
        Returns either the login link OR the session expired banner (whichever is visible).
        """
        login_link = self.page.locator("a[href='/notes/app/login']")
        expired_banner = self.page.get_by_test_id("alert-message").filter(
            has_text="Your session has expired"
        )
        return login_link.or_(expired_banner)
