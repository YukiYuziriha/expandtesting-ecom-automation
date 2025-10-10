# tests/smoke/test_home_page.py
from playwright.sync_api import Page, expect
from pages.home_page import HomePage


def test_search_bar(page: Page):
    home_page = HomePage(page)
    home_page.load()
    home_page.search_for("agile")

    expect(home_page.book_titles).to_have_count(1)
