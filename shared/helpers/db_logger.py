import sqlite3
import pathlib
import time

DB_PATH = pathlib.Path("data/test_results.db")


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=5000")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nodeid TEXT,
                outcome TEXT,
                duration_ms INTEGER,
                browser TEXT,
                failure_message TEXT,
                test_name TEXT
            )
        """)


def log_test_run(
    nodeid: str,
    outcome: str,
    browser: str,
    failure_message: str | None = None,
    test_name: str | None = None,
    duration_ms: int | None = None,
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        max_attempts = 3
        delay = 0.1
        for attempt in range(max_attempts):
            try:
                conn.execute(
                    """
                    INSERT INTO test_runs (
                        nodeid, outcome, browser, failure_message, test_name, duration_ms
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (nodeid, outcome, browser, failure_message, test_name, duration_ms),
                )
                conn.commit()
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_attempts - 1:
                    time.sleep(delay)
                    continue
                else:
                    print(f"Database error after {attempt + 1} attempts: {e}")
                    break
            except sqlite3.Error as e:
                print(f"Non-retryable database error: {e}")
                break
