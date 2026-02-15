# Task: Remove InfluxDB Integration

- [x] Planning and Issue Creation
  - [x] Create User Story [issue.md](file:///Users/divya/Documents/projects/homeautomation/monitor/docs/issues/004/issue.md)
  - [x] Create [task.md](file:///Users/divya/.gemini/antigravity/brain/696af47b-c149-49d7-bcb4-780ed7f9fd90/task.md)
  - [x] Create [implementation_plan.md](file:///Users/divya/.gemini/antigravity/brain/696af47b-c149-49d7-bcb4-780ed7f9fd90/implementation_plan.md)
- [/] Implementation
  - [x] Update `monitor_all.sh` (remove InfluxDB start and fix tmux layout)
  - [x] Update `scripts/poll_evohome_standalone.py` (remove InfluxDB logic)
  - [x] Update `scripts/poll_energymeter.py` (remove InfluxDB logic)
  - [x] Update `scripts/poll_openweathermap.py` (remove InfluxDB logic)
  - [x] Remove InfluxDB-related helper scripts
- [/] Verification
  - [x] Verify `monitor_all.sh` starts 3 panes correctly
  - [x] Verify polling scripts run without InfluxDB errors
- [x] Documentation
  - [x] Update `README.md` and other docs
  - [x] Create [walkthrough.md](file:///Users/divya/Documents/projects/homeautomation/monitor/docs/issues/004/walkthrough.md)

# Standardize CLI Arguments (Issue #9)
- [ ] Planning
  - [x] Create implementation plan
- [x] Execution
  - [x] Implement `argparse` in `poll_evohome_standalone.py`
  - [x] Implement table display and keyboard interaction
- [x] Verification
  - [x] Verify new CLI options and table view
