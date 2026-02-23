import os
import sys
import getpass
import shutil
import tempfile
import textwrap
import subprocess
import argparse
from pathlib import Path

PLIST_NAME = "com.vanmahajan.mesura.plist"
PLIST_PATH = f"/Library/LaunchDaemons/{PLIST_NAME}"

def get_project_dir():
    return Path.cwd().absolute()

def get_logs_dir():
    return get_project_dir() / "logs"

def do_install(use_uvx=False):
    actual_user = os.environ.get("SUDO_USER", getpass.getuser())
    if actual_user == "root":
        print("Could not determine your actual user. Please run without sudo.")
        sys.exit(1)

    project_dir = get_project_dir()
    python_dir = Path(sys.executable).parent
    
    if use_uvx:
        # If running via uvx, we want the daemon to execute uvx explicitly 
        # so it resolves the latest version rather than relying on an ephemeral cache path.
        uvx_path = shutil.which("uvx") or "uvx"
        prog_args = f"<string>{uvx_path}</string>\n                <string>--from</string>\n                <string>dvm-mesura</string>\n                <string>mesura-all</string>"
    else:
        # Locate the mesura-all script inside the virtual environment
        mesura_all_path = python_dir / "mesura-all"
        if not mesura_all_path.exists():
            mesura_all_path = shutil.which("mesura-all")
            
        if not mesura_all_path:
            print("Could not find 'mesura-all' executable. Using python module instead.")
            prog_args = f"<string>{sys.executable}</string>\n                <string>-m</string>\n                <string>dvm_mesura.main</string>"
        else:
            prog_args = f"<string>{mesura_all_path}</string>"

    plist_content = textwrap.dedent(f"""\
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>Label</key>
            <string>com.vanmahajan.mesura</string>
            
            <key>UserName</key>
            <string>{actual_user}</string>

            <key>ProgramArguments</key>
            <array>
                {prog_args}
            </array>

            <key>WorkingDirectory</key>
            <string>{project_dir}</string>

            <key>EnvironmentVariables</key>
            <dict>
                <key>PATH</key>
                <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:{python_dir}</string>
            </dict>

            <key>RunAtLoad</key>
            <true/>

            <key>KeepAlive</key>
            <true/>

            <key>StandardOutPath</key>
            <string>{project_dir}/logs/daemon.out</string>
            <key>StandardErrorPath</key>
            <string>{project_dir}/logs/daemon.err</string>
        </dict>
        </plist>
    """)

    print(f"Preparing to install LaunchDaemon for user '{actual_user}'.")
    print(f"Working Directory: {project_dir}")
    print("\nThis requires sudo privileges. You may be prompted for your password.")
    
    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".plist") as tmp:
        tmp.write(plist_content)
        tmp_path = tmp.name

    try:
        subprocess.run(["sudo", "-k", "launchctl", "unload", "-w", PLIST_PATH], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "cp", tmp_path, PLIST_PATH], check=True)
        subprocess.run(["sudo", "chown", "root:wheel", PLIST_PATH], check=True)
        subprocess.run(["sudo", "chmod", "644", PLIST_PATH], check=True)
        subprocess.run(["sudo", "launchctl", "load", "-w", PLIST_PATH], check=True)
        print("\nSuccess! The daemon has been installed and started.")
    except subprocess.CalledProcessError as e:
        print(f"\nError installing daemon: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def do_uninstall():
    print("Uninstalling daemon...")
    try:
        subprocess.run(["sudo", "launchctl", "unload", "-w", PLIST_PATH], stderr=subprocess.DEVNULL)
        subprocess.run(["sudo", "rm", "-f", PLIST_PATH], check=True)
        print("Success! Daemon uninstalled.")
    except subprocess.CalledProcessError as e:
        print(f"\nError uninstalling daemon: {e}")

def do_unload():
    print("Unloading daemon (temporarily stopping)...")
    try:
        subprocess.run(["sudo", "launchctl", "unload", "-w", PLIST_PATH], check=True)
        print("Success! Daemon unloaded.")
    except subprocess.CalledProcessError as e:
        print(f"\nError unloading daemon: {e}")

def do_check():
    print("Checking daemon status...")
    try:
        result = subprocess.run(["sudo", "launchctl", "list"], capture_output=True, text=True, check=True)
        if "com.vanmahajan.mesura" in result.stdout:
            for line in result.stdout.splitlines():
                if "com.vanmahajan.mesura" in line:
                    print(f"Daemon found: {line.strip()}")
                    break
        else:
            print("Daemon 'com.vanmahajan.mesura' is NOT running or loaded.")
    except subprocess.CalledProcessError as e:
        print(f"Error checking status: {e}")

def do_logs():
    logs_dir = get_logs_dir()
    err_log = logs_dir / "daemon.err"
    out_log = logs_dir / "daemon.out"
    
    print("=== Daemon Logs ===")
    if err_log.exists():
        print(f"\n[Error Log: {err_log}]")
        subprocess.run(["tail", "-n", "20", str(err_log)])
    else:
        print("\nNo error log found.")
        
    if out_log.exists():
        print(f"\n[Standard Log: {out_log}]")
        subprocess.run(["tail", "-n", "20", str(out_log)])
    else:
        print("\nNo standard log found.")

def main():
    if sys.platform != "darwin":
        print("The daemon management script is only supported on macOS.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Manage the mesura-all macOS LaunchDaemon.")
    parser.add_argument("--install", action="store_true", help="Install and start the LaunchDaemon")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall and remove the LaunchDaemon")
    parser.add_argument("--unload", action="store_true", help="Temporarily stop (unload) the LaunchDaemon")
    parser.add_argument("--check", action="store_true", help="Check if the LaunchDaemon is running")
    parser.add_argument("--logs", action="store_true", help="Tail the last 20 lines of daemon logs")
    parser.add_argument("--uvx", action="store_true", help="Configure the daemon to explicitly run via 'uvx dvm-mesura' instead of a hardcoded path. Crucial if installing from an ephemeral uvx environment.")
    
    args = parser.parse_args()
    
    if args.install:
        do_install(use_uvx=args.uvx)
    elif args.uninstall:
        do_uninstall()
    elif args.unload:
        do_unload()
    elif args.check:
        do_check()
    elif args.logs:
        do_logs()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
