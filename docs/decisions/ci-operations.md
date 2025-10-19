## CI/CD Operations Decision One-Pager

- **Context**
  - GitHub Actions runs lint, type-check, and Playwright suites on every PR.
  - Goal: keep green main, sub-6-minute feedback, rich artifacts on failure.
  - Pre-commit enforces Ruff, MyPy, detect-secrets locally before push.

- **Options Considered**
  - Single job running lint + tests sequentially.
    - ✅ Simple, low maintenance.
    - ❌ Slower feedback, hard to parallelize browsers.
  - Split jobs: lint/type-check, Playwright matrix for browsers.
    - ✅ Faster signal, can run Chromium + Firefox concurrently.
    - ❌ Slightly more YAML complexity.
  - Nightly-only browser matrix, PRs run smoke tests.
    - ✅ Faster PRs.
    - ❌ Risk shipping regressions to main.

- **Decision**
  - PR workflow runs Ruff → MyPy → Playwright tests in parallelized mode (`-n auto`) for Chromium/Firefox.
  - Capture Playwright traces/screenshots/videos on failure only; retain ≥7 days.
  - Enforce pre-commit (Ruff fix, Ruff format, detect-secrets) before commits.
  - Randomize test order (`pytest-randomly`) to expose hidden dependencies.

- **Consequences**
  - ✅ Consistent, timely CI signal; failures surface with actionable artifacts.
  - ✅ Keeps pipeline under 6 minutes through parallelization/caching.
  - ✅ Secrets scanning + linting gate regressions early.
  - ⚠️ Requires managing GitHub Actions cache + pinned versions regularly.
  - ⚠️ Must monitor flake rate (<2%) and quarantine failing cases promptly.

- **Next Review Trigger**
  - Revisit when suite runtime exceeds 6 minutes, when adding new browsers/devices, or after major dependency upgrades.
