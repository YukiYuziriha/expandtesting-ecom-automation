## Notes App: сессии и последовательность в CI

- Контекст
  - Тестируемое приложение Notes даёт аутентифицированные UI‑ и API‑флоу. Некоторые действия в UI (например, logout) иногда сбрасывают серверную сессию и в других контекстах.
  - В параллельных запусках это проявляется как неожиданный выход из аккаунта в тестах, которые сами к logout не прикасались.

- Наблюдение
  - В редких прогонах logout в параллели сбрасывает сессии других тестов. Это даёт флейки в CI при параллельном запуске.
  - Мы не управляем серверным поведением (это внешний продукт), частота зависит от внешних условий.

- Риск
  - Параллельные тесты, которые делают logout или другие действия, ломающие сессию, могут цеплять соседние тесты, даже если у них свои браузерные контексты.
  - Итог: ложные падения и недетерминированные фейлы.

- Политика и смягчение
  - Тесты, которые делают logout или инвалидируют сессию, помечены `@pytest.mark.seq_only`, чтобы не запускаться вместе с остальными UI‑тестами.
  - CI для Notes UI использует параллельные матрицы с разными пользователями:
    1) Все не‑`seq_only` в матрице браузеров (Chromium + Firefox) с `-n auto`, `--profile profile1`.
    2) Параллельно `seq_only` в отдельной матрице, последовательно в каждой джобе, с разными профилями (Firefox → `profile2`, Chromium → `profile3`).
  - Так сохраняем скорость параллели и убираем перекрёстное влияние: сценарии, которые ломают сессии, живут на отдельных аккаунтах и в последовательной ноге.

- Дополнительные меры
  - Блокировка рекламы включается только для UI‑маркированных тестов, чтобы снизить шум; API‑тесты не инициализируют Playwright.
  - Желательно чистить данные после каждого теста (API и UI), плюс держать сессионную подстраховку удаления заметок.
  - Рандомизация порядка (`pytest-randomly`) остаётся включённой, чтобы подсвечивать скрытые зависимости вне `seq_only`.

- Что дальше
  - Если сервер начнёт жёстко привязывать сессии к контексту, последовательную матрицу можно будет вернуть в общую параллельную.
  - Отдельные тестовые пользователи или более жёсткий контроль окружения могут ещё снизить шанс разделяемых сессий.

---

## Notes App: Session Behavior & CI Sequencing

- Context
  - The Notes application under test exposes authenticated UI and API flows. Some UI actions (notably logout) appear to invalidate server-side session state across contexts occasionally.
  - In parallel execution, this can manifest as unexpected sign-outs in otherwise isolated tests when multiple contexts are active concurrently.

- Observation
  - Sometimes when logout happens during parallel test runs, it affects other tests by clearing their sessions too. This happens occasionally (in a small percentage of runs) and causes flaky test failures in CI when running tests in parallel.
  - These events are beyond our direct control (3rd-party target), and their frequency varies with upstream conditions.

- Risk
  - Parallel tests that perform logout or similar state-invalidating actions can impact other in-flight tests, violating test isolation even with separate browser contexts.
  - Result: false negatives and non-deterministic failures.

- Policy & Mitigation
  - Tests that perform logout or otherwise invalidate session state are annotated with `@pytest.mark.seq_only` to signal they must not run concurrently with other UI tests.
  - CI execution for Notes UI uses concurrent matrices with isolated users:
    1) Run all non-`seq_only` tests in a browser matrix (Chromium + Firefox) with `-n auto` and `--profile profile1`.
    2) In parallel, run `seq_only` tests in a second matrix, sequentially within each job, using distinct profiles per browser (Firefox → `profile2`, Chromium → `profile3`).
  - This preserves parallel speed and removes cross-test interference by isolating potentially state-invalidating flows with separate accounts.

- Additional Safeguards
  - Ad-blocking is attached only for UI-marked tests to reduce external noise; API tests do not initialize Playwright.
  - Per-test cleanup is preferred (API- and UI-backed) with a session-level safety net for note deletion.
  - Order randomization (`pytest-randomly`) remains enabled to highlight latent dependencies outside of `seq_only` constraints.

- Future Considerations
  - If upstream session handling becomes strictly context-bound, we can revisit merging the sequential leg back under the parallel matrix.
  - Synthetic test users or environment controls may further reduce the incidence of shared-session effects.
