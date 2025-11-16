## SQLite Observability — Test Execution Logging

This project logs every pytest test-case outcome into a local SQLite database so we can inspect failures, durations, and flaky behaviour both locally and in CI. The tables and helpers live in `shared/helpers/db_logger.py`, and the hooks are wired from `conftest.py`.

### What gets stored
- File: respects `TEST_DB_PATH` if set (e.g., `TEST_DB_PATH=/tmp/run123.db pytest ...`); otherwise defaults to `data/test_results.db`.
- Table: `test_runs` (created via `init_db()`).
  - Columns include `id`, `nodeid`, `test_name`, `browser`, `duration_ms`, `outcome`, and `failure_message`.
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
- `init_db()` ensures `data/` exists, creates the table on demand, and enables WAL mode plus a `busy_timeout` for that initial connection.
- CI deletes the DB at the start of each job, so there is no cross-run state; for historical analysis, download the failure artifact bundle after a red build.
- The helper script copies the WAL/SHM sidecar files whenever it collects artifacts so the database remains consistent when inspected offline.

### Future extensions
- Capture additional metadata (`start_ts`, `failure_type`, `run_id`) and truncate `failure_message` to keep rows lean.
- Set POSIX permissions to `0o600` after file creation to limit access on shared runners.
- Create lightweight analytics (e.g., failure rate per test) by reading the SQLite artifacts or pushing rows to a long-lived warehouse once the schema stabilizes.

