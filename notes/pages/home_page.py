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

        # Modal form elements (shared between create and edit)
        self.note_category = page.get_by_test_id("note-category")
        self.note_completed = page.get_by_test_id("note-completed")
        self.note_title = page.get_by_test_id("note-title")
        self.note_description = page.get_by_test_id("note-description")
        self.note_submit = page.get_by_test_id("note-submit")

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

        # Wait for the modal to be visible
        self.note_category.wait_for(state="visible")

        # Fill the form
        self.note_category.select_option(category)
        if completed:
            self.note_completed.check()
        else:
            self.note_completed.uncheck()

        self.note_title.fill(title)
        self.note_description.fill(description)

        self.note_submit.click()

        # Wait for the modal to close
        self.note_submit.wait_for(state="hidden")

    def delete_note(self, title: str) -> None:
        """Delete the note whose card title matches ``title``."""
        target_card = self.get_note_by_title(title)
        target_card.get_by_test_id("note-delete").click()

        # Wait for network to settle before checking for dialog
        self.page.wait_for_load_state("networkidle")

        dialog = self.page.get_by_test_id("note-delete-dialog")
        dialog.wait_for(state="visible", timeout=10000)

        dialog.get_by_test_id("note-delete-confirm").click()
        dialog.wait_for(state="hidden")

    def edit_note(
        self,
        title: str,
        new_title: str,
        new_description: str,
        new_category: str = "Home",
        completed: bool = False,
    ) -> None:
        """Edit the note whose card title matches ``title``."""
        target_card = self.get_note_by_title(title)

        # Ensure the card and button are visible before clicking
        target_card.wait_for(state="visible")
        edit_button = target_card.get_by_test_id("note-edit")
        edit_button.wait_for(state="visible")
        edit_button.click()

        # Wait for the modal to be visible
        self.note_category.wait_for(state="visible")
        self.note_completed.wait_for(state="attached", timeout=10000)

        # Fill the form
        self.note_category.select_option(new_category)

        if completed:
            self.note_completed.check()
        else:
            self.note_completed.uncheck()

        self.note_title.fill(new_title)
        self.note_description.fill(new_description)

        self.note_submit.click()

        # Wait for the modal to close
        self.note_submit.wait_for(state="hidden")

    def is_note_present(self, title: str) -> bool:
        """Return True if a note with the given title is visible on the page."""
        try:
            note_card = self.get_note_by_title(title)
            note_card.wait_for(state="visible", timeout=2000)
            return True
        except Exception:
            return False

    def get_all_note_titles(self) -> list[str]:
        """Return a list of all visible note card titles on the page."""
        self.note_card_title.wait_for(state="visible", timeout=5000)
        titles = []
        for card in self.note_card.all():
            try:
                title_text = card.locator(
                    "[data-testid='note-card-title']"
                ).text_content()
                if title_text:
                    titles.append(title_text.strip())
            except Exception:
                pass
        return titles
