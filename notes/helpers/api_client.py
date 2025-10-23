# shared/helpers/api_client.py
import requests
from typing import Literal

GET = "GET"
POST = "POST"
PUT = "PUT"
PATCH = "PATCH"
DELETE = "DELETE"


class ApiClient:
    VALID_CATEGORIES = {"Home", "Work", "Personal"}
    CategoryType = Literal["Home", "Work", "Personal"]

    def __init__(
        self, BASE_URL_API: str, *, timeout: float | tuple[float, float] = 15.0
    ) -> None:
        self.base_url = BASE_URL_API
        self.token: str | None = None
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        *,
        data: dict | None = None,
        json: dict | None = None,
        params: dict | None = None,
        timeout: float | tuple[float, float] | None = None,
    ) -> dict:
        url = f"{self.base_url}{path}"
        headers = {}
        if self.token:
            headers["x-auth-token"] = self.token
        response = requests.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout or self.timeout,
        )
        response.raise_for_status()
        if not response.content:
            return {}
        return response.json()

    def login_user(self, email: str, password: str) -> dict:
        path = "/users/login"
        data = {"email": email, "password": password}

        result = self._request(POST, path, data=data)
        self.token = result["data"]["token"]
        return result

    def create_note(
        self, title: str, description: str, category: CategoryType = "Home"
    ) -> dict:
        path = "/notes"

        if category not in self.VALID_CATEGORIES:
            cats = sorted(self.VALID_CATEGORIES)
            opts = (
                (", ".join(f"'{c}'" for c in cats[:-1]) + f", or '{cats[-1]}'")
                if len(cats) > 1
                else f"'{cats[0]}'"
            )
            raise ValueError(f"Invalid category: {category}. Must be one of: {opts}")
        data = {"title": title, "description": description, "category": category}

        result = self._request(POST, path, data=data)
        return result

    def delete_note(self, note_id: str) -> dict:
        path = f"/notes/{note_id}"

        return self._request(DELETE, path)

    def get_all_notes(self) -> dict:
        path = "/notes"

        return self._request(GET, path)
