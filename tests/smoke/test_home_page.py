# tests/smoke/test_home_page.py
from playwright.sync_api import Page, expect
from pages.home_page import HomePage


def test_search_bar(page: Page) -> None:
    home_page = HomePage(page)
    home_page.load()
    home_page.search_for("agile")
    expect(home_page.book_titles).to_have_count(1)


def test_first_book_to_cart_updates_badge(page: Page) -> None:
    home_page = HomePage(page)
    home_page.load()

    assert home_page.read_cart_count() == 0

    home_page.add_book_to_cart_by_index(0)
    page.wait_for_load_state("domcontentloaded")

    assert home_page.read_cart_count() == 1
