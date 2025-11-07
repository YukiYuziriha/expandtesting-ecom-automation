# conftest.py
import json
import os
from pathlib import Path
from typing import Any, Dict, Generator

import pytest

from playwright.sync_api import Page
from shared.helpers.ad_blocker import handle_route
from shared.helpers.db_logger import log_test_run, init_db


@pytest.fixture
def page(page: Page):
    """Override the default Playwright page fixture to block ads."""
    page.route("**/*", handle_route)
    yield page


TEST_USERS_FILE = Path("shared/test_data/test_users.json")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options for the test suite."""
    parser.addoption(
        "--profile",
        action="store",
        default="profile1",
        help="Name of the test user profile to use (default: profile1).",
    )


@pytest.fixture(scope="session")
def profile_name(pytestconfig: pytest.Config, test_users: dict) -> str:
    """Resolve the active profile name from CLI options and validate it exists."""
    profile = pytestconfig.getoption("profile")
    if profile not in test_users:
        available = ", ".join(sorted(test_users))
        raise pytest.UsageError(
            f"Unknown profile '{profile}'. Available profiles: {available}."
        )
    return profile


class _MaskedStr(str):
    """String type that preserves value but masks its repr for safe logging."""

    def __new__(cls, value: str, masked: str) -> "_MaskedStr":  # type: ignore[override]
        obj = str.__new__(cls, value)  # type: ignore[misc]
        obj._masked = masked  # type: ignore[attr-defined]
        return obj

    def __repr__(self) -> str:  # pragma: no cover - small utility
        # Use repr of the masked variant so quotes/escapes are consistent
        masked = getattr(self, "_masked", "***")  # type: ignore[attr-defined]
        return repr(masked)


def _mask_email(value: str) -> str:
    try:
        name, domain = value.split("@", 1)
    except ValueError:
        return "***"
    visible = name[:1] if name else ""
    return f"{visible}***@{domain}"


def _mask_card(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    tail = digits[-4:] if len(digits) >= 4 else "****"
    return f"**** **** **** {tail}"


_SENSITIVE_KEYS = {
    "password",
    "email",
    "token",
    "auth_token",
    "x-auth-token",
    "authorization",
    "card_number",
    "cvc",
    "api_key",
    "apikey",
    "client_secret",
    "secret",
}


def _redact_in_repr(data: Any, parent_key: str | None = None) -> Any:
    """Recursively wrap sensitive string values so their repr is masked.

    The underlying value remains intact (useful for UI/API calls), but pytest's
    failure output and any accidental prints won't expose secrets.
    """
    if isinstance(data, dict):
        redacted: Dict[Any, Any] = {}
        for k, v in data.items():
            redacted[k] = _redact_in_repr(v, str(k).lower())
        return redacted
    if isinstance(data, list):
        return [_redact_in_repr(v, parent_key) for v in data]
    if isinstance(data, str):
        key = (parent_key or "").lower().replace("-", "_")
        if key in _SENSITIVE_KEYS:
            masked: str
            if "email" in key:
                masked = _mask_email(data)
            elif "card" in key:
                masked = _mask_card(data)
            elif key in {"cvc"}:
                masked = "***"
            else:
                masked = "***"
            return _MaskedStr(data, masked)
        return data
    return data


@pytest.fixture(scope="session")
def test_users() -> dict:
    """Load test user credentials and ensure secrets are redacted in logs.

    Sources:
    - Env var TEST_USERS_JSON (preferred for CI)
    - Fallback JSON file at shared/test_data/test_users.json
    """
    raw = os.getenv("TEST_USERS_JSON")
    if raw:
        try:
            loaded = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("TEST_USERS_JSON secret is not valid JSON.") from exc
        return _redact_in_repr(loaded)

    if TEST_USERS_FILE.is_file():
        with TEST_USERS_FILE.open() as f:
            loaded = json.load(f)
        return _redact_in_repr(loaded)

    raise FileNotFoundError(
        "Test user credentials were not provided. Set the TEST_USERS_JSON env "
        "variable or create shared/test_data/test_users.json."
    )


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session: pytest.Session) -> None:
    init_db()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo
) -> Generator[None, Any, None]:
    """Capture test outcome and log to database."""
    outcome: Any = yield
    report = outcome.get_result()
    if call.when != "call":
        return

    browser_option = item.config.getoption("browser", default="unknown")
    if isinstance(browser_option, (list, tuple)):
        browser = browser_option[0] if browser_option else "unknown"
    elif isinstance(browser_option, str) and browser_option:
        browser = browser_option
    else:
        browser = "unknown"

    failure_message = str(report.longrepr) if report.failed else None

    log_test_run(
        nodeid=item.nodeid,
        outcome=report.outcome,
        browser=browser,
        failure_message=failure_message,
        test_name=item.name,
    )
