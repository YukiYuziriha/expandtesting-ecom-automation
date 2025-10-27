# pages/profile_page.py
from playwright.sync_api import Page, TimeoutError
from bookstore.pages.base_page import BasePage


class ProfilePage(BasePage):
    """Page Object for the user Profile page with order history."""

    URL = "/bookstore/user/profile"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        self.order_confirmation_banner = self.page.locator("#flash.alert.alert-success")
        self.delete_all_orders_button = self.page.locator("#deleteOrdersBtn")
        self.order_cards = self.page.locator("div.card[data-testid]")

    def load(self) -> None:
        """Navigate to the profile page."""
        self._safe_goto(self.URL)

    def delete_all_orders_if_present(self) -> None:
        """Click the delete button only when orders exist and accept the confirmation dialog."""
        try:
            self.delete_all_orders_button.wait_for(state="visible", timeout=1000)
        except TimeoutError:
            return

        # Set up dialog handler that only accepts confirmation dialogs
        def handle_dialog(dialog):
            if "delete all orders" in dialog.message.lower():
                dialog.accept()
            else:
                dialog.dismiss()  # Safety: dismiss unexpected dialogs

        self.page.on("dialog", handle_dialog)
        self.delete_all_orders_button.click()

        # Wait for orders to disappear
        self.order_cards.first.wait_for(state="detached", timeout=5000)
