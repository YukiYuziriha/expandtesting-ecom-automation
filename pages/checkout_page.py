# pages.checkout_page.py
from playwright.sync_api import Page
from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Page Object for the ExpandTesting Bookstore Checkout page."""

    URL = "https://practice.expandtesting.com/bookstore/checkout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # Billing section
        self.name_input = self.page.locator("#name")
        self.address_input = self.page.locator("#address")

        # Card section
        self.card_name_input = self.page.locator("#card-name")
        self.card_number_input = self.page.locator("#card-number")
        self.card_expiry_month_input = self.page.locator("#card-expiry-month")
        self.card_expiry_year_input = self.page.locator("#card-expiry-year")
        self.card_cvc_input = self.page.locator("#card-cvc")

        # Submit button
        self.purchase_button = self.page.get_by_test_id("purchase")

    def load(self) -> None:
        """Navigate to the checkout page."""
        self._safe_goto(self.URL)

    def fill_and_submit(
        self,
        name: str,
        address: str,
        card_name: str,
        card_number: str,
        exp_month: int,
        exp_year: int,
        cvc: str,
    ) -> None:
        """
        Fill all billing and card fields and submit the purchase form.
        Waits for DOM content to load after submission.
        """
        # Fill billing details
        self.name_input.fill(name)
        self.address_input.fill(address)

        # Fill card details
        self.card_name_input.fill(card_name)
        self.card_number_input.fill(card_number)
        self.card_expiry_month_input.fill(str(exp_month))
        self.card_expiry_year_input.fill(str(exp_year))
        self.card_cvc_input.fill(cvc)

        # Submit form
        self.purchase_button.click()
        self.page.wait_for_load_state("domcontentloaded")
