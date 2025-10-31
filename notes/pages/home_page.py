from playwright.sync_api import Page, Locator
from notes.pages.base_page import BasePage


class HomePage(BasePage):
    """Page Object for the ExpandTesting Notes Home page."""

    URL = "/notes/app"

    def __init__(self, page: Page) -> None:
        super().__init__(page)

        # Notes list
        self.note_card = page.get_by_test_id("note-card")
        self.note_card_title = page.get_by_test_id("note-card-title")
        self.note_card_description = page.get_by_test_id("note-card-description")

        # Add Note modal trigger
        self.add_note_button = page.get_by_test_id("add-new-note")

    def load(self) -> None:
        """Navigate to the Notes home page."""
        self.goto(self.URL)

    def get_note_by_title(self, title: str) -> Locator:
        """Return the first note card whose title matches the given title."""
        return self.note_card.filter(
            has=self.note_card_title.filter(has_text=title)
        ).first

    def get_note_card_title(self, note_card: Locator) -> Locator:
        """Return the title locator scoped within a given note card."""
        return note_card.locator(self.note_card_title)

    def get_note_card_description(self, note_card: Locator) -> Locator:
        """Return the description locator scoped within a given note card."""
        return note_card.locator(self.note_card_description)

    def create_note(
        self,
        title: str,
        description: str,
        category: str = "Home",
        completed: bool = False,
    ) -> None:
        """Open the Add Note modal, fill the form, and submit."""
        self.add_note_button.click()

        # Wait for the category select to be visible (it's in the modal)
        category_select = self.page.get_by_test_id("note-category")
        category_select.wait_for(state="visible")

        # Get the other form elements
        completed_checkbox = self.page.get_by_test_id("note-completed")
        title_input = self.page.get_by_test_id("note-title")
        description_input = self.page.get_by_test_id("note-description")
        submit_button = self.page.get_by_test_id("note-submit")

        category_select.select_option(category)
        if completed:
            completed_checkbox.check()
        else:
            completed_checkbox.uncheck()

        title_input.fill(title)
        description_input.fill(description)

        submit_button.click()

        # Wait for the modal to close
        submit_button.wait_for(state="hidden")
