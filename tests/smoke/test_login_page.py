# tests/smoke/test_login_page.py
import pytest
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage
import json


@pytest.fixture(scope="module")
def test_users() -> dict:
    with open("test_data/test_users.json") as f:
        return json.load(f)


def test_login_page_invalid_creds(page: Page) -> None:
    login_page = LoginPage(page)
    login_page.load()

    # Test empty creds
    login_page.login("", "")
    expect(login_page.credentials_error_message).to_be_visible()

    # Test Invalid creds
    login_page.login("dawsa", "awd")
    expect(login_page.credentials_error_message).to_be_visible()


def test_login_page_correct_creds(page: Page, test_users: dict) -> None:
    login_page = LoginPage(page)
    login_page.load()

    user = test_users["profile1"]
    login_page.login(user["email"], user["password"])
    page.wait_for_url("**/profile")
    expect(page.get_by_role("heading", name="Profile")).to_be_visible()
    expect(page.get_by_role("heading", name="My Orders")).to_be_visible()
