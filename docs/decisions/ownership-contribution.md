## Как устроены владение и вклад (одна страница)

- **Контекст**
  - Сейчас проект поддерживает один человек, но в будущем ожидаются контрибьюторы.
  - `CODEOWNERS` закрепляет `@YukiYuziriha` за всем репозиторием и путями `tests/`, `pages/`, `.github/`.
  - Нужны простые и прозрачные правила веток, ревью и релизов, чтобы `main` оставалась зелёной.

- **Рассмотренные варианты**
  - Лёгкие рекомендации только в README.
    - ✅ Минимальная поддержка.
    - ❌ Оставляет много неопределённости для авторов и ревьюеров.
  - Conventional Commits + feature‑ветки + обязательные PR‑ревью.
    - ✅ Хорошо стыкуется с текущим CI, упрощает автоматизацию changelog/versioning.
    - ❌ Требует дисциплины при написании сообщений коммитов.
  - Git‑flow (develop/main с release‑ветками).
    - ✅ Структурированные релизы.
    - ❌ Слишком тяжёлый процесс для текущего масштаба.

- **Решение**
  - Использовать feature‑ветки формата `<type>/<topic>` (`feat/checkout`, `chore/codeowners`).
  - Требовать PR с зелёным CI; `CODEOWNERS` автоматически запрашивает ревью.
  - Следовать Conventional Commits; squash‑merge допустим, если заголовок коммита сохраняется.
  - Защитить `main`: прямые пуши запрещены, нужны все зелёные проверки.
  - Зафиксировать чек‑лист для контрибьюторов: перед PR гонять `ruff`, `mypy`, `pytest -q`, при необходимости прикладывать скриншоты/trace.

- **Последствия**
  - ✅ Предсказуемый процесс ревью и понятная история изменений.
  - ✅ Гигиена релизов сохраняется даже при появлении новых участников.
  - ✅ Проще автоматизировать релиз‑ноты и changelog.
  - ⚠️ Есть небольшой оверхед даже для мелких фиксов; смягчается шаблоном PR‑чек‑листа.

- **Повод пересмотреть**
  - Когда появятся новые мейнтейнеры, появятся автоматические релизы или нужно будет синхронизировать несколько репозиториев.

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
