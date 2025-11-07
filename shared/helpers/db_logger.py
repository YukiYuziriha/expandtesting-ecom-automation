import sqlite3
import pathlib

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
                start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_ts TIMESTAMP,
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
) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute(
                """
                INSERT INTO test_runs (
                    nodeid, outcome, browser, failure_message, test_name
                    )
                    VALUES (?, ?, ?, ?, ?)
            """,
                (nodeid, outcome, browser, failure_message, test_name),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error logging test run: {e}")
