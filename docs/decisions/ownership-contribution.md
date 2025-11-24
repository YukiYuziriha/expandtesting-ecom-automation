## Решение по процессу владения и вклада (одна страница)

- **Контекст**
  - Проект пока поддерживается одним человеком, но ожидаются будущие контрибьюторы.
  - `CODEOWNERS` закрепляет `@YukiYuziriha` за всем репозиторием и путями `tests/`, `pages/`, `.github/`.
  - Нужны прозрачные правила ветвления, ревью и релизов, чтобы `main` оставалась зеленой.

- **Рассмотренные варианты**
  - Легковесные рекомендации (только README).
    - ✅ Минимальная поддержка.
    - ❌ Оставляет неопределенность для авторов и ревьюеров.
  - Conventional Commits + feature-ветки + обязательные PR-ревью.
    - ✅ Соответствует контракту CI, упрощает автоматизацию changelog/versioning.
    - ❌ Требует дисциплины в формулировке коммитов.
  - Git-flow (develop/main с release-ветками).
    - ✅ Структурированные релизы.
    - ❌ Избыточно для текущего масштаба.

- **Решение**
  - Использовать feature-ветки `<type>/<topic>` (`feat/checkout`, `chore/codeowners`).
  - Требовать PR с проходящим CI; `CODEOWNERS` автоматически запрашивает ревью.
  - Следовать Conventional Commits; squash merge допустим при сохранении заголовков коммитов.
  - Защищать `main`: прямые пуши запрещены, зеленые проверки обязательны.
  - Зафиксировать чек-лист контрибьюций: запуск `ruff`, `mypy`, `pytest -q`, при необходимости приложить скриншоты/trace.

- **Последствия**
  - ✅ Предсказуемый процесс ревью и понятная история изменений.
  - ✅ Гигиена релизов сохраняется даже при появлении новых участников.
  - ✅ Проще автоматизировать релиз-ноты и changelog.
  - ⚠️ Незначительное увеличение расходов для мелких фиксов; смягчается шаблоном PR-чек-листа.

- **Повод пересмотреть**
  - При добавлении новых мейнтейнеров, включении автоматических релизов или расширении до нескольких репозиториев.

---

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
