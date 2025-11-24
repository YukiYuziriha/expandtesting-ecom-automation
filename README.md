
# End-to-End E-Commerce Automation with Observability

### One-Sentence Summary
> Engineered a production-grade UI test automation framework in Python using Playwright and Pytest to validate a complete e-commerce user journey on [ExpandTesting.com](https://practice.expandtesting.com/), featuring parallel execution, cached authentication, and artifact reporting in a CI/CD pipeline.

[![CI Pipeline](https://github.com/YukiYuziriha/expandtesting-ecom-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/YukiYuziriha/expandtesting-ecom-automation/actions)

---

## ► Why This Project Matters

This isn't just a collection of test scripts; it's a demonstration of a professional automation strategy designed to be **maintainable, scalable, and CI-native**. It directly addresses the core competencies required for a modern QA Automation Engineer role by proving:

* **Architectural Thinking**: A strict Page Object Model (POM) ensures the framework is maintainable and separates test logic from UI implementation.
* **CI/CD Proficiency**: The entire test suite runs in a parallelized GitHub Actions workflow on every PR, providing fast feedback with video and trace artifacts on failure.
* **Framework Resilience**: Locators are built to be "apocalypse-proof," relying on semantic and structural selectors (`role`, `data-testid`, `type=submit`) rather than brittle UI text or CSS classes.
* **Performance Optimization**: Implements a session-scoped, cached authentication fixture (`storage_state` with `FileLock`), eliminating repetitive UI logins and reducing total execution time by over 90%.

---

## ✨ Key Features & Architecture

| Feature                  | Implementation & Rationale                                                                                                                                                                                                                                                               |
| :----------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Page Object Model (POM)** | Strict separation of concerns. Tests contain workflows and assertions; Page Objects contain locators and actions. This makes tests readable and the framework easy to maintain.                                                                                                    |
| **Cached Authentication** | A session-scoped Pytest fixture logs in **once per session**, saving the state to a file. Each test then creates a new, isolated browser context from this state, achieving both **speed and 100% test isolation**.                                                                  |
| **Resilient Locators** | The locator strategy is anchored to the **most stable attributes** of the DOM—those that define an element's *purpose*, not its appearance. This means prioritizing semantic HTML (`form`, `button[type='submit']`), accessibility contracts (`aria-label`), and developer test hooks (`data-testid`) over brittle selectors like CSS classes or UI text. |
| **CI/CD Pipeline** | PRs run the full E2E suite in a two‑browser matrix (Chromium + Firefox). Pushes run a fast smoke subset on a single browser (Chromium) to keep feedback under ~6 minutes. All jobs upload trace/video artifacts on failure. Linting (`ruff`) and type‑checking (`mypy`) gate regressions. |
| **Observability** | Every pytest run logs metadata into `data/test_results.db` via SQLite; the helper script `scripts/ci/sqlite_observability.sh` keeps the file clean per run, and CI uploads the DB (plus videos/traces/screens) on failure for fast forensic analysis. See `docs/sqlite_observability.md`. |
| **Ad & Tracker Blocking** | A layered defense combines network-level request blocking with DOM-level ad dismissal to create a stable, noise-free test environment.                                                                                                                                                      |
| **Marker-Driven Suites** | All tests are tagged with pytest markers (`smoke`, `ui`, `api`, `e2e`, `bookstore`, `notes`) so CI can run targeted suites and developers can slice the matrix locally with a single flag. |

---

## 🛠️ Tech Stack

| Component         | Choice            | Why                                                                                                                            |
| :---------------- | :---------------- | :----------------------------------------------------------------------------------------------------------------------------- |
| **Language** | Python 3.12       | Industry standard for QA; readable and powerful.                                                                               |
| **Framework** | Playwright + Pytest | Modern, async-aware, with minimal flakiness and rich features like auto-waits, tracing, and a first-class test runner.         |
| **CI/CD** | GitHub Actions    | Tightly integrated with the repository, zero infrastructure overhead, and easily configurable for parallel, cross-browser execution. |
| **Linting & Formatting** | Ruff & MyPy       | Enforces code quality, consistency, and type safety, preventing common errors before they merge.                               |
| **Parallelization** | `pytest-xdist`    | Significantly reduces pipeline execution time by running tests concurrently.                                                  |

---

## 🚀 Local Setup & Execution

### **1. Prerequisites**
* Python 3.12+
* `git`

### **2. Installation**
```bash
# 1. Clone the repository
git clone [https://https://github.com/YukiYuziriha/expandtesting-ecom-automation/tree/refactor-pom](https://github.com/YukiYuziriha/expandtesting-ecom-automation/tree/refactor-pom)
cd expandtesting-ecom-automation

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Playwright browsers and system dependencies
playwright install --with-deps
````

### **2.1 Provide Test Credentials**
The suite looks for credentials in the `TEST_USERS_JSON` environment variable or a local `shared/test_data/test_users.json` file (git-ignored). Profiles are keyed by name (e.g., `profile1`, `profile2`), and you can select one at runtime with `pytest --profile=<name>`. If no profile is specified, `profile1` is used by default.

> ℹ️ Notes API tests exercise the live service at `https://practice.expandtesting.com/notes/api`. Make sure the credentials you supply are valid for that environment and that outbound network access is available. Tests create temporary notes and the fixtures clean them up automatically after each run.

### **2.2 Offline Mock API Mode (Notes Tests)**
The Notes API tests can run in **offline mode** using a hermetic, mocked API backend. This is useful for:
- Running tests without external network dependencies
- Local development and verification
- Hermetic CI jobs that don't rely on external services

**Enable offline mode:**
```bash
# Run Notes API tests with mocked backend (no network required)
export NOTES_OFFLINE=1
pytest -m "notes and api" -v

# Run without offline mode (hit real API)
unset NOTES_OFFLINE
pytest -m "notes and api" -v
```

**What the mock provides:**
- In-memory store for notes (CRUD operations)
- Auth validation (login, token checks, 401 for unauthorized access)
- Deterministic responses (400/404 for missing resources, 422 for invalid categories)
- Negative test coverage (wrong credentials, invalid payloads, resource not found)

The mock is **automatically enabled when `NOTES_OFFLINE=1`** and only affects tests marked with `@pytest.mark.notes`. All other tests run normally.

### **3. Running Tests**

```bash
# Recommended full run (flakiness-aware)
# 1) Run non-sequential tests in parallel for speed
pytest -m "not seq_only" -v -n auto

# 2) Then run sequential-only tests (these can invalidate global session state)
pytest -m "seq_only" -v

# Run only smoke checks (bookstore UI + notes API)
pytest -m "smoke"

# Focus on a specific surface
pytest -m "bookstore and ui"
pytest -m "notes and api"

# Run tests in a specific file (headed, for debugging)
pytest bookstore/tests/test_purchase_journey.py --headed

# Run tests only in a specific browser
pytest tests/ -v --browser firefox

# Switch the active test user profile (defaults to profile1)
pytest -k login --profile=profile2
```

-----

## 🧭 CI at a Glance

- Push (fast): smoke tests only
  - Bookstore UI and Notes UI on a single browser (Chromium), parallelized, excluding `seq_only` to avoid session cross‑talk.
  - Notes API smoke (no browser dependency).
- Pull Request (full): complete coverage
  - Bookstore UI on Chromium + Firefox in parallel.
  - Notes UI runs two matrices concurrently: (1) parallel matrix for all non‑`seq_only` with `--profile profile1`, and (2) a sequential matrix for `seq_only` (Firefox → `profile2`, Chromium → `profile3`).
  - Notes Hybrid UI+API runs as a dedicated job concurrently (Chromium + Firefox), filtered with `-m "hybrid"`, using `--profile profile1`.
  - Notes API full.
- Artifacts: for any failure, CI uploads Playwright traces, videos, and screenshots for fast debugging.

Why: Short push runs keep iteration snappy and reduce exposure to third‑party flakiness. PRs get full, multi‑browser confidence. `seq_only` groups flows like logout can invalidate sessions; running them concurrently in a separate matrix with distinct user profiles preserves isolation while reducing wall‑clock time.

Details: see docs/decisions/ci-operations.md and docs/decisions/notes-app-session-behavior.md

## 📺 Live Demo

[![Watch the demo](https://img.youtube.com/vi/YlflQdfF60c/0.jpg)](https://youtu.be/YlflQdfF60c)

A 20-second walkthrough of the authenticated purchase journey running locally with `--headed` mode.
