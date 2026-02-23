# User Story: Fix Grafana `SQLITE_BUSY` error

**As a user**, I want to be able to save my Grafana dashboards without encountering SQLite locking errors, so that I don't lose my work and can manage my home automation visualizations reliably.

## Problem Description
When saving a dashboard, Grafana returns: `database is locked (5) (SQLITE_BUSY)`.
This typically occurs when Grafana's internal SQLite database is under heavy load from concurrent tasks like the alerting engine or multiple datasource queries.

## Acceptance Criteria
- Dashboards can be saved without locking errors.
- Grafana's internal database is optimized for concurrent access using WAL mode.
- The `SQLITE_BUSY` error no longer appears in `grafana.log` during normal operation.
