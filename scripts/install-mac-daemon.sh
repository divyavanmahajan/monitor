#!/usr/bin/env bash
set -e

# Ensure we're running as root or can sudo
if [ "$EUID" -ne 0 ]; then
  echo "This script requires root privileges to install the LaunchDaemon."
  echo "Please run: sudo bash $0"
  exit 1
fi

# We need the username of the actual user who invoked sudo
ACTUAL_USER=${SUDO_USER:-$(whoami)}
if [ "$ACTUAL_USER" = "root" ]; then
    echo "Could not determine the original user. Please log in as a normal user and use sudo."
    exit 1
fi

# Get the path to this project (assuming the script is inside scripts/ directory)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# We should try to find `uv` for the user. Since we're running as root, `which uv` might give root's uv.
# Let's run a shell as the actual user to find uv
UV_PATH=$(su - "$ACTUAL_USER" -c 'which uv')

if [ -z "$UV_PATH" ]; then
    # Fallback to common locations if `which` didn't find it in the non-interactive shell profile
    if [ -x "/Users/$ACTUAL_USER/.cargo/bin/uv" ]; then
        UV_PATH="/Users/$ACTUAL_USER/.cargo/bin/uv"
    elif [ -x "/opt/homebrew/bin/uv" ]; then
        UV_PATH="/opt/homebrew/bin/uv"
    elif [ -x "/usr/local/bin/uv" ]; then
        UV_PATH="/usr/local/bin/uv"
    else
        echo "Error: Could not find 'uv' command for user $ACTUAL_USER."
        echo "Please ensure uv is installed and in the user's PATH."
        exit 1
    fi
fi

echo "Detected parameters:"
echo "User:            $ACTUAL_USER"
echo "Project Dir:     $PROJECT_DIR"
echo "uv Path:         $UV_PATH"

PLIST_NAME="com.mesura.monitor.plist"
PLIST_PATH="/Library/LaunchDaemons/$PLIST_NAME"

echo "Creating plist at $PLIST_PATH..."

cat <<EOF > "$PLIST_PATH"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.mesura.monitor</string>
    
    <key>UserName</key>
    <string>$ACTUAL_USER</string>

    <key>ProgramArguments</key>
    <array>
        <string>$UV_PATH</string>
        <string>run</string>
        <string>mesura-all</string>
    </array>

    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin</string>
    </dict>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <true/>

    <key>StandardOutPath</key>
    <string>$PROJECT_DIR/logs/daemon.out</string>
    <key>StandardErrorPath</key>
    <string>$PROJECT_DIR/logs/daemon.err</string>
</dict>
</plist>
EOF

echo "Setting permissions..."
chown root:wheel "$PLIST_PATH"
chmod 644 "$PLIST_PATH"

echo "Creating logs directory..."
mkdir -p "$PROJECT_DIR/logs"
chown "$ACTUAL_USER" "$PROJECT_DIR/logs"

echo "Loading LaunchDaemon..."
# Unload first just in case
launchctl unload -w "$PLIST_PATH" 2>/dev/null || true
launchctl load -w "$PLIST_PATH"

echo "Done! The mesura-all daemon is now installed and running in the background."
echo "Check logs at:"
echo "  $PROJECT_DIR/logs/daemon.out"
echo "  $PROJECT_DIR/logs/daemon.err"
