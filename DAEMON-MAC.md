# macOS LaunchDaemon Setup for dvm-mesura

To run the `mesura-all` monitoring suite continuously in the background—even if the user is logged out or after a system restart—you can configure it as a macOS `LaunchDaemon`.

macOS uses `launchd` for managing background services. 
- **LaunchAgents** run only when a specific user is logged in.
- **LaunchDaemons** run in the background completely independent of user logins (e.g. system boot).

## Automated Built-in Tool

The easiest way to manage the LaunchDaemon is to use the built-in `mesura-daemon` CLI tool, which handles everything seamlessly. 

It will automatically discover your username, project directory, set permissions, and manage the `launchctl` commands. (Since it interacts with `launchd`, you'll be prompted for your local macOS password when running it).

### 1. Install & Start

If you have installed the package globally as a tool using `uv`:

```bash
# Step 1: Install the package globally
uv tool install dvm-mesura

# Step 2: Install and start the daemon in the background
mesura-daemon --install
```

If you are using it locally through a project directory with `uv run`:

```bash
# Install and start the daemon in the background
uv run mesura-daemon --install
```

If you installed or are running the tool using `uvx` directly (which creates temporary isolated environments that are eventually cleared from cache), you **must** supply the `--uvx` flag! This configures the daemon so that it triggers `uvx --from dvm-mesura mesura-all` natively instead of hardcoding an ephemeral cache path into the Launchd configuration:

```bash
# Install using uvx
uvx dvm-mesura mesura-daemon --install --uvx
```

### 2. Checking and Managing Logs

Once installed, you can check its status or view the logs. *(Remember to use the appropriate prefix like `uv run` or `uvx dvm-mesura` if you didn't install the tool globally).*

```bash
# Check if the daemon is active
mesura-daemon --check

# View the last 20 lines of the daemon's log files
mesura-daemon --logs
```

### 3. Uninstall / Stop

If you need to temporarily stop it or completely remove it:

```bash
# Temporarily unload (stop) the daemon without removing it completely
mesura-daemon --unload

# Utterly uninstall and remove the daemon from the system
mesura-daemon --uninstall
```