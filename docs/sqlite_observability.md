## SQLite Observability — Test Execution Logging

This project logs every pytest test-case outcome into a local SQLite database so we can inspect failures, durations, and flaky behaviour both locally and in CI. The tables and helpers live in `shared/helpers/db_logger.py`, and the hooks are wired from `conftest.py`.

### What gets stored
- File: `data/test_results.db` (override with `TEST_DB_PATH`).
- Table: `test_runs` (created via `init_db()`).
  - Columns include `nodeid`, `test_name`, `file`, `duration_ms`, `browser`, `outcome`, `failure_message` (truncated), and timestamp metadata.
- Writes happen in `pytest_runtest_makereport` (only for the `call` phase), so setup/teardown noise is excluded.
- No secrets or payloads are persisted—see `_redact_in_repr` in `conftest.py` for masking.

### Local workflow
1. **Prep the DB**: `./scripts/ci/sqlite_observability.sh prep`
2. **Run any pytest command** (hooks create the schema on demand).
3. **Verify**: `./scripts/ci/sqlite_observability.sh verify`
4. **Inspect** with `sqlite3 data/test_results.db "SELECT test_name, outcome FROM test_runs ORDER BY start_ts DESC LIMIT 10;"`.
5. **Collect** (optional): `./scripts/ci/sqlite_observability.sh collect tmp/db-artifact`

### CI workflow
- Every job that runs pytest executes the helper script at three points:
  1. `prep` before tests for a clean slate.
  2. `verify` after tests (guarded with `if: always()`).
  3. `collect` + `actions/upload-artifact` only when the job fails.
- This guarantees deterministic files per run and keeps artifacts small; WAL/SHM files are copied alongside the main DB for integrity.

### Permissions & durability
- `init_db()` sets the SQLite file permissions to `0o600` on POSIX to avoid leaking metadata.
- WAL mode and `busy_timeout` are enabled on every connection so `pytest -n auto` can log concurrently without contention.
- CI deletes the DB at the start of each job, so there is no cross-run state; for historical analysis, download the failure artifact bundle or point `TEST_DB_PATH` to a persistent mount.

### Future extensions
- Add `run_id` rows via `pytest_sessionstart/finish` to correlate multiple tests within the same CI invocation.
- Create lightweight analytics (e.g., failure rate per test) by reading the SQLite artifacts or pushing rows to a long-lived warehouse once the schema stabilizes.

