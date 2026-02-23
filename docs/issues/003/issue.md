# User Story: Fix Grafana Timestamp Parsing

**As a user**, I want my Grafana dashboards to correctly parse timestamps from my SQLite databases, so that I can visualize my home automation data over time without blank or unparseable date fields.

## Problem Description
Grafana's SQLite datasource plugin cannot automatically parse ISO 8601 strings from SQLite `TEXT` columns in some cases, resulting in blank time fields in panels. This is currently happening with `weatherdata.db`. Additionally, some date-related fields like `sunrise` and `sunset` are incorrectly stored as `REAL` numbers in the `readings` table.

## Acceptance Criteria
- SQL queries in `setup-grafana.md` use `strftime` to provide a format Grafana can reliably parse.
- The `weatherdata.db` schema is documented correctly with `TEXT` for all timestamp/ISO date fields.
- Dashboards display the correct time on the X-axis.
