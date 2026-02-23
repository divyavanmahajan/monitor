# macOS LaunchDaemon Setup for dvm-mesura

To run the `mesura-all` monitoring suite continuously in the background—even if the user is logged out or after a system restart—you can configure it as a macOS `LaunchDaemon`.

macOS uses `launchd` for managing background services. 
- **LaunchAgents** run only when a specific user is logged in.
- **LaunchDaemons** run in the background completely independent of user logins (e.g. system boot).

## Automated Installation

The easiest way to install the daemon is to run the provided setup script. It automatically discovers your username, project directory, and `uv` installation path, generates the plist, sets permissions, and loads the daemon.

```bash
sudo bash scripts/install-mac-daemon.sh
```

## Manual Installation

If you prefer to configure it manually, follow the steps below.

### 1. Locate your `uv` and script paths
Because LaunchDaemons run in a stripped-down root environment, you should use absolute paths for both the `uv` tool and your project directory.

Find the absolute path to your project directory. For example:
`/Users/yourusername/Documents/projects/homeautomation/monitor`

Find the path to your `uv` binary:
```bash
which uv
```
*(Often `/Users/yourusername/.cargo/bin/uv` or `/opt/homebrew/bin/uv`)*

## 2. Create the Property List (plist) file

You need to create a `.plist` file in `/Library/LaunchDaemons/`. We'll call it `com.mesura.monitor.plist`.

Create this file (requires `sudo`):

```bash
sudo nano /Library/LaunchDaemons/com.mesura.monitor.plist
```

Paste the following content, making sure to replace `<YOUR_USERNAME>`, `<PATH_TO_PROJECT>`, and `<PATH_TO_UV>` with your actual paths:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mesura.monitor</string>
    
    <!-- Identify the user to run the process as. Required in LaunchDaemons if you don't want to run as root -->
    <key>UserName</key>
    <string><YOUR_USERNAME></string>

    <key>ProgramArguments</key>
    <array>
        <!-- Absolute path to uv executable -->
        <string><PATH_TO_UV></string>
        <string>run</string>
        <string>mesura-all</string>
    </array>

    <!-- The working directory for the application -->
    <key>WorkingDirectory</key>
    <string><PATH_TO_PROJECT></string>

    <!-- Environment Variables (Optional but recommended) -->
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <!-- Automatically restart if it crashes -->
    <key>KeepAlive</key>
    <true/>

    <!-- Log files -->
    <key>StandardOutPath</key>
    <string><PATH_TO_PROJECT>/logs/daemon.out</string>
    <key>StandardErrorPath</key>
    <string><PATH_TO_PROJECT>/logs/daemon.err</string>
</dict>
</plist>
```

*(Ensure the `/logs` directory exists inside your project folder: `mkdir -p <PATH_TO_PROJECT>/logs`)*

## 3. Set Permissions

LaunchDaemons *must* be owned by root and have specific permissions, or `launchd` will refuse to load them.

```bash
sudo chown root:wheel /Library/LaunchDaemons/com.mesura.monitor.plist
sudo chmod 644 /Library/LaunchDaemons/com.mesura.monitor.plist
```

## 4. Load and Start the Daemon

To load the daemon into the system:

```bash
sudo launchctl load -w /Library/LaunchDaemons/com.mesura.monitor.plist
```

This ensures `mesura-all` will now start up seamlessly in the background any time the Mac is powered on.

## Controlling the Daemon

Check if it is running:
```bash
sudo launchctl list | grep com.mesura.monitor
```

View the logs:
```bash
tail -f <PATH_TO_PROJECT>/logs/daemon.err
```

Unload or Stop the daemon temporarily:
```bash
sudo launchctl unload -w /Library/LaunchDaemons/com.mesura.monitor.plist
```
