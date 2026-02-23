# Task: Refactor Home Automation Monitor (Issue #13)

## Research and Planning
- [x] Analyze existing monitors and extract common patterns
- [x] Design the new architecture (Sources, Sinks, Controller)
- [x] Define the configuration schema
- [x] Create implementation plan

## Infrastructure
- [x] Implement base classes for Monitors and Backends
- [x] Implement Common Helpers (CLI parsing, logging)

## Storage Backends (Sinks)
- [x] Implement SQLite Sink
- [x] Implement CSV Sink
- [ ] Implement InfluxDB Sink (optional placeholder)

## Monitors (Sources)
- [x] Refactor Energy Meter Monitor
- [x] Refactor Weather Monitor
- [x] Refactor Evohome Monitor

## Controller
- [x] Implement Async Master Controller loop
- [x] Implement per-monitor polling logic

## Finalization
- [x] Update main entry points
- [x] Verify functionality with tests
- [x] Update documentation

## SQLite Concurrency Security
- [x] Update `Backend` protocol to be asynchronous
- [x] Implement `asyncio.Lock` and WAL mode in `SQLiteBackend`
- [x] Add concurrency tests to verify thread safety
