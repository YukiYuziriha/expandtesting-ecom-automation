## Ownership & Contribution Flow Decision One-Pager

- **Context**
  - Solo-maintained project with future collaborators expected.
  - CODEOWNERS assigns `@YukiYuziriha` to entire repo plus `tests/`, `pages/`, `.github/`.
  - Need clear branching, review, and release expectations to keep main green.

- **Options Considered**
  - Lightweight guidance (README only).
    - ✅ Minimal upkeep.
    - ❌ Leaves ambiguity for contributors and reviewers.
  - Conventional Commits + feature branches + required PR reviews.
    - ✅ Aligns with CI contract, easy to automate changelog/versioning.
    - ❌ Requires discipline in commit crafting.
  - Git-flow (develop/main with release branches).
    - ✅ Structured releases.
    - ❌ Overkill for current repo scale.

- **Decision**
  - Use feature branches named `<type>/<topic>` (`feat/checkout`, `chore/codeowners`).
  - Require PRs with CI passing before merge; CODEOWNERS auto-request review.
  - Follow Conventional Commits; squash merges allowed if commit titles preserved.
  - Protect `main`: no direct pushes, green checks mandatory.
  - Document contribution checklist: run `ruff`, `mypy`, `pytest -q`, attach context screenshots/traces if relevant.

- **Consequences**
  - ✅ Predictable review flow, easier audit of changes.
  - ✅ Maintains release hygiene even with new contributors.
  - ✅ Simplifies automation (release notes, changelog).
  - ⚠️ Slight overhead for small fixes; mitigate with template PR checklist.

- **Next Review Trigger**
  - Reevaluate when adding more maintainers, enabling automated releases, or expanding to multi-repo coordination.
