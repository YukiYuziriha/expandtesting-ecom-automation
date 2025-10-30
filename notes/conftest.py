# notes/conftest.py
from collections.abc import Callable, Iterator
from typing import Any
from uuid import uuid4
import os
import json
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl

import pytest
import requests
import responses  # type: ignore

from notes.helpers.api_client import ApiClient
from config import BASE_URL_API


@pytest.fixture(
    scope="function"
)  # isolate auth/token per test; switch to session for speed if safe
def api_client_auth(test_users: dict, profile_name: str) -> ApiClient:
    """Create an API client for the notes API."""
    api_client = ApiClient(BASE_URL_API)
    user = test_users[profile_name]
    api_client.login_user(email=user["email"], password=user["password"])
    return api_client


@pytest.fixture
def note_cleanup(api_client_auth: ApiClient) -> Iterator[Callable[[str], None]]:
    """Register created note ids for automatic teardown."""
    note_ids: list[str] = []

    def register(note_id: str) -> None:
        note_ids.append(note_id)

    yield register

    while note_ids:
        note_id = note_ids.pop()
        try:
            api_client_auth.delete_note(note_id)
        except requests.exceptions.HTTPError as exc:
            if exc.response is None or exc.response.status_code not in {400, 404}:
                raise


@pytest.fixture
def note_factory(
    api_client_auth: ApiClient, note_cleanup: Callable[[str], None]
) -> Callable[..., dict[str, Any]]:
    """Create a note with optional overrides and register it for cleanup."""

    def create_note(
        *,
        title: str | None = None,
        description: str | None = None,
        category: str = "Home",
    ) -> dict[str, Any]:
        generated_title = title or f"Auto Note {uuid4().hex[:8]}"
        generated_description = description or f"Auto Description {uuid4().hex[:8]}"
        response = api_client_auth.create_note(
            generated_title, generated_description, category
        )
        note_cleanup(response["data"]["id"])
        return response

    return create_note


# --- Offline Notes API mock -------------------------------------------------
# Enables running the Notes API tests without hitting the real external site.
# Activate by setting environment variable: NOTES_OFFLINE=1

NOTES_OFFLINE = os.getenv("NOTES_OFFLINE", "0") == "1"


@pytest.fixture(autouse=True)
def notes_api_mock(request) -> Iterator[None]:
    """Mock Notes API when NOTES_OFFLINE=1 so tests run without network.

    Applies only to tests marked with @pytest.mark.notes. Always yields once,
    even when mock is disabled, to satisfy generator fixture contract.
    """
    # Only affect notes tests
    if "notes" not in request.keywords:
        yield
        return

    # If offline is disabled, do nothing but still yield once
    if not NOTES_OFFLINE:
        yield
        return

    store: dict[str, dict] = {}

    def now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    def parse_body(req) -> dict:
        if not req.body:
            return {}
        if isinstance(req.body, (bytes, bytearray)):
            return dict(parse_qsl(req.body.decode()))
        if isinstance(req.body, str):
            return dict(parse_qsl(req.body))
        if isinstance(req.body, dict):
            return req.body
        return {}

    def is_authorized(req) -> bool:
        token = req.headers.get("x-auth-token") if req.headers else None
        return token == "fake-token"

    allowed_categories = {"Home", "Work"}

    def get_note_id_from_url(url: str) -> str:
        """Extract note ID from URL path."""
        match = re.search(r"/notes/([A-Za-z0-9\-]+)$", url)
        if not match:
            raise ValueError(f"Could not extract note ID from URL: {url}")
        return match.group(1)

    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        # POST /users/login
        def login_cb(req):
            data = parse_body(req)
            if data.get("password") == "wrong-password":
                return (
                    401,
                    {},
                    json.dumps({"success": False, "message": "Unauthorized"}),
                )
            return (
                200,
                {},
                json.dumps({"success": True, "data": {"token": "fake-token"}}),
            )

        rsps.add_callback(
            responses.POST,
            re.compile(r".*/notes/api/users/login$"),
            callback=lambda req, **kw: login_cb(req),
            content_type="application/json",
        )

        # Notes endpoints must be authorized
        def require_auth(handler):
            def wrapped(req, *args, **kwargs):
                if not is_authorized(req):
                    return (
                        401,
                        {},
                        json.dumps({"success": False, "message": "Unauthorized"}),
                    )
                return handler(req, *args, **kwargs)

            return wrapped

        # POST /notes (create)
        @require_auth
        def create_note_cb(req):
            data = parse_body(req)
            category = data.get("category", "Home")
            if category not in allowed_categories:
                return (
                    422,
                    {},
                    json.dumps({"success": False, "message": "Invalid category"}),
                )
            note_id = uuid4().hex[:12]
            note = {
                "id": note_id,
                "title": data.get("title", ""),
                "description": data.get("description", ""),
                "category": category,
                "completed": False,
                "created_at": now_iso(),
            }
            store[note_id] = note
            return (200, {}, json.dumps({"success": True, "data": note}))

        rsps.add_callback(
            responses.POST,
            re.compile(r".*/notes/api/notes$"),
            callback=lambda req, **kw: create_note_cb(req),
            content_type="application/json",
        )

        # GET /notes (list)
        @require_auth
        def list_notes_cb(_req):
            return (
                200,
                {},
                json.dumps({"success": True, "data": list(store.values())}),
            )

        rsps.add_callback(
            responses.GET,
            re.compile(r".*/notes/api/notes$"),
            callback=lambda req, **kw: list_notes_cb(req),
            content_type="application/json",
        )

        # GET /notes/{id}
        @require_auth
        def get_note_cb(_req, id_: str):
            note = store.get(id_)
            if not note:
                return (404, {}, json.dumps({"success": False, "message": "Not Found"}))
            return (200, {}, json.dumps({"success": True, "data": note}))

        rsps.add_callback(
            responses.GET,
            re.compile(r".*/notes/api/notes/([A-Za-z0-9\-]+)$"),
            callback=lambda req, **kw: get_note_cb(req, get_note_id_from_url(req.url)),
            content_type="application/json",
        )

        # PUT /notes/{id}
        @require_auth
        def update_note_cb(req, id_: str):
            if id_ not in store:
                return (404, {}, json.dumps({"success": False, "message": "Not Found"}))
            payload = parse_body(req)
            note = store[id_]
            note.update(
                {
                    "title": payload.get("title", note["title"]),
                    "description": payload.get("description", note["description"]),
                    "category": payload.get("category", note["category"]),
                    "completed": str(payload.get("completed", "false")).strip().lower()
                    == "true",
                }
            )
            return (200, {}, json.dumps({"success": True, "data": note}))

        rsps.add_callback(
            responses.PUT,
            re.compile(r".*/notes/api/notes/([A-Za-z0-9\-]+)$"),
            callback=lambda req, **kw: update_note_cb(
                req, get_note_id_from_url(req.url)
            ),
            content_type="application/json",
        )

        # DELETE /notes/{id}
        @require_auth
        def delete_note_cb(_req, id_: str):
            if id_ not in store:
                return (404, {}, json.dumps({"success": False, "message": "Not Found"}))
            del store[id_]
            return (200, {}, json.dumps({"success": True, "data": {}}))

        rsps.add_callback(
            responses.DELETE,
            re.compile(r".*/notes/api/notes/([A-Za-z0-9\-]+)$"),
            callback=lambda req, **kw: delete_note_cb(
                req, get_note_id_from_url(req.url)
            ),
            content_type="application/json",
        )

        # Keep the mock active for the duration of the test
        yield
