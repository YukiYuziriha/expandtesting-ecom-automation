## Логирование прогонов тестов в SQLite

Проект пишет результат каждого pytest‑теста в локальную базу SQLite, чтобы удобно разбирать падения, длительность и флейки как локально, так и в CI. Таблицы и хелперы лежат в `shared/helpers/db_logger.py`, хуки подключены из `conftest.py`.

### Что сохраняется
- Файл: если задан `TEST_DB_PATH` (например, `TEST_DB_PATH=/tmp/run123.db pytest ...`), используется он; иначе — `data/test_results.db`.
- Таблица: `test_runs` (создаётся через `init_db()`).
  - Колонки: `id`, `nodeid`, `test_name`, `browser`, `duration_ms`, `outcome`, `failure_message` (обрезка до 512 символов) и `start_ts`.
- Запись происходит в `pytest_runtest_makereport` (только фаза `call`), поэтому подготовка/очистка не шумят.
- `_redact_in_repr` (см. `conftest.py`) маскирует чувствительные данные до того, как они попадут в логи или БД.

### Локальный воркфлоу
1. **Подготовить БД**: `./scripts/ci/sqlite_observability.sh prep`.
2. **Запустить любой pytest** (хуки создадут схему при необходимости).
3. **Проверить**: `./scripts/ci/sqlite_observability.sh verify`.
4. **Посмотреть последние записи**: `sqlite3 data/test_results.db "SELECT test_name, outcome FROM test_runs ORDER BY id DESC LIMIT 10;"`.
5. **Собрать артефакт** (опционально): `./scripts/ci/sqlite_observability.sh collect tmp/db-artifact`.

### Как это работает в CI
- Каждая джоба с pytest вызывает helper‑скрипт трижды:
  1. `prep` перед тестами для чистого состояния.
  2. `verify` после тестов (под `if: always()`).
  3. `collect` + `actions/upload-artifact` только при падении джобы.
- В результате для каждого прогона получаются детерминированные файлы и небольшие артефакты; WAL/SHM копируются вместе с основной БД для целостности.

### Права и долговечность
- `init_db()` создаёт `data/`, таблицу, включает WAL и `busy_timeout`, выставляет права `0o600` (только владелец).
- CI удаляет БД в начале каждой джобы, поэтому состояния между запусками нет; для истории можно скачать артефакт после красного билда.
- Helper копирует WAL/SHM при сборе артефактов, чтобы база оставалась консистентной при офлайн‑анализе.

### Что можно развивать дальше
- Добавить метаданные (`failure_type`, `run_id`) для аналитики.
- Сделать легковесные отчёты (например, частота падений по тестам) на основе артефактных SQLite‑файлов или отправлять строки в долгоживущее хранилище после стабилизации схемы.

---

## SQLite Observability — Test Execution Logging

This project logs every pytest test-case outcome into a local SQLite database so we can inspect failures, durations, and flaky behaviour both locally and in CI. The tables and helpers live in `shared/helpers/db_logger.py`, and the hooks are wired from `conftest.py`.

### What gets stored
- File: respects `TEST_DB_PATH` if set (e.g., `TEST_DB_PATH=/tmp/run123.db pytest ...`); otherwise defaults to `data/test_results.db`.
- Table: `test_runs` (created via `init_db()`).
  - Columns include `id`, `nodeid`, `test_name`, `browser`, `duration_ms`, `outcome`, `failure_message` (truncated to 512 chars), and `start_ts`.
- Writes happen in `pytest_runtest_makereport` (only for the `call` phase), so setup/teardown noise is excluded.
- `_redact_in_repr` (see `conftest.py`) masks sensitive credentials before they ever appear in pytest logs or DB rows.

### Local workflow
1. **Prep the DB**: `./scripts/ci/sqlite_observability.sh prep`
2. **Run any pytest command** (hooks create the schema on demand).
3. **Verify**: `./scripts/ci/sqlite_observability.sh verify`
4. **Inspect** with `sqlite3 data/test_results.db "SELECT test_name, outcome FROM test_runs ORDER BY id DESC LIMIT 10;"`.
5. **Collect** (optional): `./scripts/ci/sqlite_observability.sh collect tmp/db-artifact`

### CI workflow
- Every job that runs pytest executes the helper script at three points:
  1. `prep` before tests for a clean slate.
  2. `verify` after tests (guarded with `if: always()`).
  3. `collect` + `actions/upload-artifact` only when the job fails.
- This guarantees deterministic files per run and keeps artifacts small; WAL/SHM files are copied alongside the main DB for integrity.

### Permissions & durability
- `init_db()` ensures `data/` exists, creates the table on demand, enables WAL mode plus a `busy_timeout`, and sets file permissions to `0o600` (owner read/write only).
- CI deletes the DB at the start of each job, so there is no cross-run state; for historical analysis, download the failure artifact bundle after a red build.
- The helper script copies the WAL/SHM sidecar files whenever it collects artifacts so the database remains consistent when inspected offline.

### Future extensions
- Capture additional metadata (`failure_type`, `run_id`) to enrich analytics.
- Create lightweight analytics (e.g., failure rate per test) by reading the SQLite artifacts or pushing rows to a long-lived warehouse once the schema stabilizes.
