## CI/CD: как устроены джобы (кратко)

- Контекст
  - GitHub Actions запускает линтинг, типизацию и Playwright‑наборы.
  - Цели: держать `main` зеленой, получать фидбек до 6 минут на push, собирать артефакты при сбоях и при этом не терять пользу от тестов.
  - Pre-commit локально запускает Ruff и MyPy; сканирование секретов включено.

- Какие события что запускают (текущее)
  - push (любая ветка): запускаются только smoke‑срезы
    - Bookstore UI: `-m "smoke and ui and not seq_only"` на одном браузере (`chromium`) с `-n auto`.
    - Notes UI: `-m "smoke and ui and not seq_only"` на `chromium` с `-n auto`.
    - Notes API: `-m "smoke"` (без Playwright).
    - Зачем так: быстрый фидбек и меньше флейков от внешних сайтов; `seq_only` не гоняются, чтобы не ломать общее состояние.
  - pull_request → main: полный набор тестов
    - Bookstore UI: матрица `chromium` и `firefox`.
    - Notes UI: две матрицы параллельно — (1) параллельная для не-`seq_only`, (2) последовательная для `seq_only` с изолированными профилями на каждую ногу.
    - Notes Hybrid UI+API: выделенная матрица из двух браузеров, `notes/tests/hybrid/` с `-m "hybrid"`, запускается параллельно.
    - Notes API: полный набор.

- Матрица браузеров и последовательность
  - Bookstore UI: параллельная матрица (Chromium + Firefox) для всех тестов; отдельная последовательная ветка не нужна.
  - Notes UI: параллельность с изоляцией для предсказуемого поведения и скорости:
    1) Параллельная матрица (Chromium + Firefox): `-m "not seq_only"` с `-n auto`, `--profile profile1`.
    2) Последовательная матрица (Chromium + Firefox): `-m "seq_only"` без `-n`, с отдельными профилями (Firefox → `--profile profile2`, Chromium → `--profile profile3`).
    - Обоснование: logout в Notes иногда сбрасывает сессии в других контекстах. Выделение `seq_only` с отдельными аккаунтами убирает перекрестное влияние, но при этом обе матрицы всё равно бегут параллельно.
  - Notes Hybrid: отдельная джоба `test-notes-hybrid` запускается параллельно, демонстрируя cross-layer проверки без влияния на smoke или `seq_only`. Использует `--profile profile1` и матрицу Chromium + Firefox.

- Артефакты и диагностика
  - При любом фейле загружаются Playwright traces, видео, скриншоты и `test-results/` во всех джобах.
  - Последовательные джобы используют `always()` по событию, чтобы артефакты собирались даже после падения предыдущих стадий.

- Рассмотренные варианты
  - Одна последовательная джоба с линтом и тестами: проще, но медленно; мало параллельности.
  - Всегда запускать полные матрицы на push: больше флейков и долгий runtime.
  - Ночные матрицы + push‑smoke: быстрее push, но выше риск поймать регрессию только на PR.

- Решение
  - Придерживаться стратегии push‑smoke и PR‑full, с отдельной последовательной ногой для `seq_only` в Notes.
  - Сохранять артефакты при сбое с ретеншном ≥7 дней.
  - Рандомизировать порядок тестов (`pytest-randomly`), чтобы выявлять скрытые зависимости.

- Последствия
  - ✅ Быстрые push‑циклы, меньше флейков от внешних сайтов.
  - ✅ Нормальный уровень уверенности перед merge за счёт PR‑матриц и параллельного последовательного лега.
  - ✅ При любом падении есть артефакты для разборов.
  - ⚠️ YAML чуть сложнее и нужно больше параллельных раннеров из‑за дополнительного последовательного лега.

- Триггеры для пересмотра
  - Если push‑smoke превысит ~6 минут; при добавлении браузеров/устройств; если сессии Notes стабилизируются и позволят убрать последовательное ограничение.

---

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
