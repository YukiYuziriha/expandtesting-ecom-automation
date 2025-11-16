#!/usr/bin/env bash
set -euo pipefail

DB_PATH=${TEST_DB_PATH:-"$PWD/data/test_results.db"}
DB_DIR=$(dirname "$DB_PATH")

usage() {
  cat <<EOF
Usage: $0 {prep|verify|collect <dest-dir>}
  prep     Create data directory and remove any existing SQLite artifacts.
  verify   Fail if the DB file is missing when tests were supposed to write it.
  collect  Copy DB + WAL/SHM into the provided directory (for artifacts on failure).
EOF
}

prep() {
  mkdir -p "$DB_DIR"
  rm -f "$DB_PATH" "$DB_PATH-wal" "$DB_PATH-shm"
}

verify() {
  if [ ! -f "$DB_PATH" ]; then
    echo "WARNING: $DB_PATH not found; no test rows were written."
    return 0
  fi
  sqlite3 "$DB_PATH" "SELECT name FROM sqlite_master WHERE name='test_runs';" >/dev/null
}

collect() {
  local dest="$1"
  mkdir -p "$dest"
  if [ -f "$DB_PATH" ]; then
    cp "$DB_PATH" "$dest/" || true
  fi
  for suffix in -wal -shm; do
    if [ -f "$DB_PATH$suffix" ]; then
      cp "$DB_PATH$suffix" "$dest/" || true
    fi
  done
}

case "${1:-}" in
  prep) prep ;;
  verify) verify ;;
  collect)
    shift
    [ $# -eq 1 ] || { usage; exit 1; }
    collect "$1"
    ;;
  *) usage; exit 1 ;;
esac