## Test Data & Environment Policy Decision One-Pager

- **Context**
  - UI journeys hit practice.expandtesting.com; stability depends on predictable data.
  - Need deterministic flows for carts/orders without polluting shared state.
  - Framework already blocks ads/analytics noise (per README/AGENTS.md).

- **Options Considered**
  - Live environment only, reset via UI.
    - ✅ No mocks; closest to prod.
    - ❌ Slow, brittle, risk of cross-test interference.
  - Hybrid: live for core flows, stub external/unstable services via Playwright routing.
    - ✅ Control over volatility; respects “test what we own.”
    - ❌ Requires maintaining fixtures for mocked routes.
  - Fully mocked backend with contract tests.
    - ✅ Maximum determinism.
    - ❌ Diverges from actual behavior; high maintenance.

- **Decision**
  - Run against the public ExpandTesting environment for primary flows.
  - Use Playwright `route.abort()` to block ads/trackers; `route.fulfill()` only for third-party or flaky integrations.
  - Keep user credentials and cart configs in `test_data/`; manage sensitive data via `.secrets.baseline`.
  - Fresh browser context per test, seeded from cached auth state set up once per session.

- **Consequences**
  - ✅ Tests reflect real UI/API behavior while remaining stable.
  - ✅ Data fixtures localized to tests; easy to reset or extend.
  - ✅ Deterministic execution thanks to isolated contexts and network filters.
  - ⚠️ Still dependent on public env uptime; add retries around session bootstrap if outages increase.
  - ⚠️ Need to review stubs periodically so they match real contracts.

- **Next Review Trigger**
  - Reassess when environment SLA degrades, when new third-party integrations appear, or before adding write-heavy admin flows.
