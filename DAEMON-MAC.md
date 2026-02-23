# macOS LaunchDaemon Setup for dvm-mesura

To run the `mesura-all` monitoring suite continuously in the background—even if the user is logged out or after a system restart—you can configure it as a macOS `LaunchDaemon`.

macOS uses `launchd` for managing background services. 
- **LaunchAgents** run only when a specific user is logged in.
- **LaunchDaemons** run in the background completely independent of user logins (e.g. system boot).

## Automated Built-in Tool

The easiest way to manage the LaunchDaemon is to use the built-in `mesura-daemon` CLI tool, which handles everything directly from `uv`. 

It will automatically discover your username, project directory, set permissions, and manage the `launchctl` commands. (Since it interacts with `launchd`, you'll be prompted for your local macOS password when running it).

```bash
If you installed or are running the tool using `uvx` directly (which creates temporary isolated environments that are eventually cleared from cache), you **must** supply the `--uvx` flag! This configures the daemon so that it triggers `uvx dvm-mesura` natively instead of hardcoding an ephemeral cache path into the Launchd configuration:

```bash
uvx dvm-mesura mesura-daemon --install --uvx
```

### Checking and Managing logs
