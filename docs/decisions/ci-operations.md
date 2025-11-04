## CI/CD Operations Decision One-Pager

- Context
  - GitHub Actions orchestrates linting, type-checking, and Playwright suites.
  - Goals: keep main green, sub-6-minute push feedback, artifacts on failure, minimize flake exposure while preserving signal.
  - Pre-commit enforces Ruff and MyPy locally; secret scanning stays on.

- Event Scoping (Current)
  - push (any branch): run smoke subsets only
    - Bookstore UI: `-m "smoke and ui and not seq_only"` on a single browser (`chromium`) with `-n auto`.
    - Notes UI: `-m "smoke and ui and not seq_only"` on `chromium` with `-n auto`.
    - Notes API: `-m "smoke"` (no Playwright dependency).
    - Rationale: fast developer feedback and reduced flake exposure from third-party sites; excludes `seq_only` flows that could invalidate shared state.
  - pull_request → main: run full suite
    - Bookstore UI: matrix over `chromium` and `firefox`.
    - Notes UI: run two matrices concurrently — (1) parallel matrix for non-`seq_only`, and (2) sequential matrix for `seq_only` — using isolated user profiles per leg.
    - Notes Hybrid UI+API: dedicated two‑browser matrix running `notes/tests/hybrid/` with `-m "hybrid"` in parallel with other jobs.
    - Notes API: full suite.

- Browser Matrix and Sequencing
  - Bookstore UI: parallel matrix (Chromium + Firefox) for all tests; no special sequencing required.
  - Notes UI: concurrency with isolation to maintain determinism and speed:
    1) Parallel matrix (Chromium + Firefox): `-m "not seq_only"` with `-n auto`, `--profile profile1`.
    2) Sequential matrix (Chromium + Firefox): `-m "seq_only"` with no `-n`, using distinct profiles per browser (e.g., Firefox → `--profile profile2`, Chromium → `--profile profile3`).
    - Rationale: Notes logout flow can invalidate sessions across contexts intermittently. Running seq_only in their own matrix with distinct test users removes cross-talk while enabling both matrices to run at the same time for reduced wall‑clock.
  - Notes Hybrid: explicit job `test-notes-hybrid` runs concurrently to showcase cross‑layer validation without impacting smoke or seq_only. Uses `--profile profile1` and browser matrix over Chromium + Firefox.

- Artifacts & Diagnostics
  - On any failure, upload Playwright traces, videos, screenshots, and `test-results/` across all jobs.
  - Sequential jobs use unconditional execution (`always()`) gated by event so artifacts are captured even if previous legs fail.

- Options Considered
  - Single sequential job with lint + tests: simple but slow; poor parallelization.
  - Always run full matrices on push: higher flake exposure and runtime cost.
  - Nightly-only matrices with push smoke: faster pushes but risk regressions on PRs.

- Decision
  - Adopt push-smoke and PR-full strategy with Notes-specific sequential gating as above.
  - Keep artifacts-on-failure with ≥7-day retention.
  - Randomize test order (`pytest-randomly`) to surface hidden dependencies.

- Consequences
  - ✅ Faster push cycles; lower flake impact from external sites.
  - ✅ Full pre-merge confidence via PR matrices with concurrent sequential leg.
  - ✅ Actionable artifacts captured for any failure mode.
  - ⚠️ Slightly more YAML complexity and additional concurrent runners for the sequential leg.

- Next Review Triggers
  - If push smoke exceeds ~6 minutes; if adding browsers/devices; if Notes session handling stabilizes and allows removal of sequential gating.
