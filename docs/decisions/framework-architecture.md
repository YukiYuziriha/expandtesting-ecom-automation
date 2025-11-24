## Архитектура фреймворка и инструменты (кратко)

- **Контекст**
  - Проверить e-commerce путь ExpandTesting стабильной и поддерживаемой автоматизацией.
  - Сбалансировать скорость итераций, выразительные проверки и удобство CI для Python-инженеров.
  - Повторно использовать инвестиции в Playwright при сохранении изоляции и детерминизма тестов.

- **Рассмотренные варианты**
  - Playwright + Pytest (Python 3.12) с Page Object Model.
    - ✅ Автоожидания, поддержка async, первоклассный tracing, соответствие экосистеме Python.
    - ✅ Фикстуры Pytest обеспечивают изоляцию, параметризацию, параллельность (`xdist`).
    - ❌ Требуется дисциплина для защиты от хрупких локаторов и аккуратного шаринга авторизации.
  - Selenium + Pytest.
    - ✅ Большое коммьюнити и экосистема.
    - ❌ Больше ручных ожиданий, медленнее выполнение, слабее tracing.
  - Cypress (JS) + API-hooks.
    - ✅ Отличный DX, time-travel отладка.
    - ❌ Смена стека на JS, слабее интеграция с Python, высокий порог переноса.

- **Решение**
  - Принять Playwright + Pytest со строгим POM и кешированной аутентификацией.
  - Хранить повторно используемые локаторы и действия в `pages/`, оставлять проверки в `tests/`.
  - Авторизоваться один раз за сессию через storage state + `FileLock`; каждый тест получает новый контекст.

- **Последствия**
  - ✅ Быстрые, надежные тесты с автоожиданиями и богатыми артефактами.
  - ✅ Четкое разделение ответственности; легко расширять новыми сценариями.
  - ✅ Детерминированная авторизация ускоряет прогоны примерно на 90% по сравнению с UI-логином в каждом тесте.
  - ⚠️ Нужен контроль гигиены локаторов (следовать порядку из AGENTS.md, если появится).
  - ⚠️ POM требует дисциплины ревью, чтобы логика не мигрировала в Page Objects.

- **Повод пересмотреть**
  - При миграции на новые устройства/браузеры или если кеш аутентификации станет хрупким (например, изменится схема сессии).

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
