# Tasks

- [x] Research Grafana `SQLITE_BUSY` error
    - [x] Check Grafana logs
    - [x] Verify if multiple processes are accessing `grafana.db`
- [x] Create GitHub issue for the bug
- [x] Propose and implement fix
    - [x] Enable WAL mode for `grafana.db`
    - [x] Check for rogue processes locking the DB
- [x] Verify fix
