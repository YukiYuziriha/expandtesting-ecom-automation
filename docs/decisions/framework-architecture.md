## Framework Architecture & Tooling Decision One-Pager

- **Context**
  - Validate ExpandTesting e-commerce journey with stable, maintainable automation.
  - Balance fast iteration, rich assertions, and CI friendliness for Python engineers.
  - Reuse existing Playwright investment while keeping tests isolated and deterministic.

- **Options Considered**
  - Playwright + Pytest (Python 3.12) with Page Object Model.
    - ✅ Native auto-waits, async-friendly, first-class tracing, Python ecosystem alignment.
    - ✅ Pytest fixtures for isolation, parametrization, parallelization (`xdist`).
    - ❌ Requires guarding against flaky selectors and sharing auth responsibly.
  - Selenium + Pytest.
    - ✅ Broad community, existing tooling.
    - ❌ Higher maintenance for waits, slower execution, weaker tracing.
  - Cypress (JS) + API hooks.
    - ✅ Excellent DX, time-travel debugging.
    - ❌ Requires switching language stack, weaker Python integration, heavier porting cost.

- **Decision**
  - Adopt Playwright + Pytest with a strict Page Object Model and cached authentication.
  - Store reusable selectors and actions in `pages/`, keep assertions in `tests/`.
  - Authenticate once per session via storage state + `FileLock`; each test gets a fresh context.

- **Consequences**
  - ✅ Fast, reliable tests with automatic waiting and rich artifacts.
  - ✅ Clear separation of concerns; easy to extend with more flows.
  - ✅ Deterministic auth improves runtime by ~90% vs. UI login every test.
  - ⚠️ Requires vigilance on locator hygiene (follow AGENTS.md ordering).
  - ⚠️ POM abstraction needs disciplined review to avoid logic creeping into page objects.

- **Next Review Trigger**
  - Revisit when migrating to another device/browser matrix, or if auth caching becomes brittle (e.g., upstream session schema change).
