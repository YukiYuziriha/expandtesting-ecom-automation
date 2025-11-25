## Архитектура фреймворка и инструменты (кратко)

- **Контекст**
  - Нужно проверять e‑commerce‑путь ExpandTesting стабильной и поддерживаемой автоматизацией.
  - Важно балансировать скорость итераций, нормальные проверки и удобный CI для Python‑инженеров.
  - Хочется переиспользовать Playwright, но при этом держать тесты изолированными и предсказуемыми.

- **Рассмотренные варианты**
  - Playwright + Pytest (Python 3.12) с Page Object Model.
    - ✅ Автоожидания, поддержка async, удобный tracing, нативно ложится на Python‑экосистему.
    - ✅ Фикстуры Pytest дают изоляцию, параметризацию и параллельность (`xdist`).
    - ❌ Нужна дисциплина: аккуратно выбирать локаторы и не раздувать шаринг авторизации.
  - Selenium + Pytest.
    - ✅ Большое комьюнити и экосистема.
    - ❌ Больше ручных ожиданий, медленнее выполнение, слабее tracing.
  - Cypress (JS) + API‑хуки.
    - ✅ Крутой DX, time‑travel‑отладка.
    - ❌ Переезд на JS‑стек, хуже интеграция с Python, дорогой перенос.

- **Решение**
  - Взять Playwright + Pytest со строгим POM и кешированной аутентификацией.
  - Повторно используемые локаторы и действия хранить в `pages/`, проверки оставлять в `tests/`.
  - Логиниться один раз за сессию через storage state + `FileLock`, а каждому тесту выдавать новый контекст.

- **Последствия**
  - ✅ Тесты бегут быстро, с автоожиданиями и нормальными артефактами.
  - ✅ Разделение ответственности прозрачное; новые сценарии добавляются без боли.
  - ✅ Кеш авторизации ускоряет прогоны примерно на 90% по сравнению с UI‑логином в каждом тесте.
  - ⚠️ Нужен контроль гигиены локаторов (следовать договорённостям в AGENTS.md, если появится).
  - ⚠️ Для POM важен ревью: следить, чтобы бизнес‑логика не уезжала в Page‑объекты.

- **Повод пересмотреть**
  - При смене матрицы устройств/браузеров или если кеш авторизации станет хрупким (например, изменится схема сессий).

---

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
