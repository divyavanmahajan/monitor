# Fix Grafana `SQLITE_BUSY` Error

The user is encountering `SQLITE_BUSY` errors when saving Grafana dashboards. This is likely due to concurrent write operations in the internal SQLite database (e.g., the alerting engine). Enabling Write-Ahead Logging (WAL) mode will improve concurrency support.

## Proposed Changes

### [Component Name: Grafana Configuration]

#### [MODIFY] [grafana.db](file:///opt/homebrew/var/lib/grafana/grafana.db)
We will enable WAL mode on the database.

1. Stop Grafana: `brew services stop grafana`
2. Enable WAL mode: `sqlite3 /opt/homebrew/var/lib/grafana/grafana.db "PRAGMA journal_mode=WAL;"`
3. Restart Grafana: `brew services start grafana`

## Verification Plan

### Manual Verification
1. Log in to Grafana at `http://localhost:3000`.
2. Try to save a dashboard while the monitor scripts are running.
3. Check `/opt/homebrew/var/log/grafana/grafana.log` for any new `SQLITE_BUSY` errors.
4. Verify WAL mode is active: `sqlite3 /opt/homebrew/var/lib/grafana/grafana.db "PRAGMA journal_mode;"` (should return `wal`).
