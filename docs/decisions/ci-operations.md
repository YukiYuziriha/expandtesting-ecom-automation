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
    - Notes UI: matrix parallel for non-`seq_only`, then gated sequential jobs (see below).
    - Notes API: full suite.

- Browser Matrix and Sequencing
  - Bookstore UI: parallel matrix (Chromium + Firefox) for all tests; no special sequencing required.
  - Notes UI: two-phase execution to maintain determinism:
    1) Parallel matrix (Chromium + Firefox): `-m "not seq_only"` with `-n auto`.
    2) Sequential gating: run `seq_only` tests after the entire matrix completes — first on Firefox, then on Chromium.
    - Rationale: Notes logout flow can invalidate sessions across contexts intermittently; isolating these flows avoids cross-test interference.

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
  - ✅ Full pre-merge confidence via PR matrices and sequential gating.
  - ✅ Actionable artifacts captured for any failure mode.
  - ⚠️ Slightly more YAML complexity and an extra sequential phase for Notes.

- Next Review Triggers
  - If push smoke exceeds ~6 minutes; if adding browsers/devices; if Notes session handling stabilizes and allows removal of sequential gating.
