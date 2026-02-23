import os
import sys
import getpass
import shutil
import tempfile
import textwrap
import subprocess
import argparse
from pathlib import Path
from dvm_mesura.setup import setup_wizard
from dotenv import load_dotenv
import certifi

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
    env_path = project_dir / ".env"
    
    print(f"Configuring environment in {project_dir}...")
    setup_wizard(env_path)
    
    # Reload env to get DATA_DIR for reporting
    load_dotenv(env_path, override=True)
    data_dir_name = os.getenv("DATA_DIR", "data")
    data_dir_abs = (project_dir / data_dir_name).absolute()

    python_dir = Path(sys.executable).parent
    
    if use_uvx:
        # If running via uvx, we want the daemon to execute uvx explicitly 
        # so it resolves the latest version rather than relying on an ephemeral cache path.
        uvx_path = shutil.which("uvx") or "uvx"
        prog_args = f"<string>{uvx_path}</string>\n                <string>--from</string>\n                <string>dvm-mesura</string>\n                <string>mesura-all</string>"
    else:
        uv_path = shutil.which("uv")
        if not uv_path:
            # Fallback path if 'uv' isn't in sudo's PATH
            uv_path = f"/Users/{actual_user}/.cargo/bin/uv"
            if not Path(uv_path).exists():
                uv_path = "/opt/homebrew/bin/uv"
                
        prog_args = f"<string>{uv_path}</string>\n                <string>run</string>\n                <string>mesura-all</string>"

    embed_env = input("Do you want to embed your environment variables directly in the LaunchDaemon? [Y/n]: ").lower() != 'n'
    env_vars_plist = ""
    
    if embed_env:
        print("\nWARNING: Variables embedded in the LaunchDaemon plist can be read by any user on this system (stored in /Library/LaunchDaemons/).")
        # Load the latest values decided during setup
        load_dotenv(env_path, override=True)
        relevant_vars = [
            "ENERGY_API_URL", "ENERGY_INTERVAL", 
            "OPENWEATHER_API_KEY", "WEATHER_INTERVAL", 
            "LATITUDE", "LONGITUDE",
            "EVOHOME_USERNAME", "EVOHOME_EMAIL", "EVOHOME_PASSWORD", "EVOHOME_INTERVAL",
            "DATA_DIR", "SEPARATE_DBS"
        ]
        
        env_dict_lines = []
        for var in relevant_vars:
            val = os.getenv(var)
            if val is not None:
                # Plist keys and values must be escaped strings in the dict
                env_dict_lines.append(f"                <key>{var}</key>")
                env_dict_lines.append(f"                <string>{val}</string>")
        
        if env_dict_lines:
            env_vars_plist = "\n".join(env_dict_lines)
            
    # Always include PATH and SSL_CERT_FILE
    path_val = f"/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:/opt/homebrew/bin:{python_dir}"
    env_vars_plist += f"\n                <key>PATH</key>\n                <string>{path_val}</string>"
    env_vars_plist += f"\n                <key>SSL_CERT_FILE</key>\n                <string>{certifi.where()}</string>"

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
{env_vars_plist}
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
        print("-" * 65)
        print(f"DATA RESIDENCY:")
        print(f"Your monitoring data will be stored in:")
        print(f"  {data_dir_abs}")
        print("-" * 65)
        
        # macOS TCC Warning
        if "Documents" in str(project_dir) or "Desktop" in str(project_dir) or "Downloads" in str(project_dir):
            print("\n" + "!" * 65)
            print("WARNING: macOS Privacy Protections (TCC) detected!")
            print(f"Your project directory acts from a protected folder:")
            print(f"-> {project_dir}")
            print("\nLaunchDaemons run in the background as root and macOS STRICTLY blocks")
            print("background daemons from reading/writing to ~/Documents or ~/Desktop.")
            print("\nIf you see 'PermissionError: [Errno 1] Operation not permitted' in")
            print("the logs, the easiest fix is moving your project folder somewhere else:")
            print(f"   mv {project_dir} /Users/{actual_user}/mesura")
            print(f"   cd /Users/{actual_user}/mesura")
            print("   uv run mesura-daemon --install")
            print("!" * 65)
            
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

def do_start():
    print("Loading daemon (starting)...")
    try:
        if not Path(PLIST_PATH).exists():
            print(f"Error: Daemon not installed. Use --install first.")
            return
        subprocess.run(["sudo", "launchctl", "load", "-w", PLIST_PATH], check=True)
        print("Success! Daemon started.")
    except subprocess.CalledProcessError as e:
        print(f"\nError starting daemon: {e}")

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

def do_env_check():
    project_dir = get_project_dir()
    env_path = project_dir / ".env"
    
    print("=== Environment Variable Check ===")
    print(f"Project Directory: {project_dir}")
    print(f".env File Path:    {env_path}")
    
    if env_path.exists():
        print(f"\n--- .env Contents ---")
        try:
            with open(env_path, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"Error reading .env: {e}")
    else:
        print(f"\n[!] .env file does not exist.")

    # List relevant environment variables
    relevant_vars = [
        "ENERGY_API_URL", "ENERGY_INTERVAL", 
        "OPENWEATHER_API_KEY", "WEATHER_INTERVAL", 
        "LATITUDE", "LONGITUDE",
        "EVOHOME_USERNAME", "EVOHOME_EMAIL", "EVOHOME_PASSWORD", "EVOHOME_INTERVAL",
        "DATA_DIR", "SEPARATE_DBS"
    ]
    
    print("\n--- Active Environment Variables (OS Process) ---")
    # Load env so we see what the module thinks is active
    load_dotenv(env_path, override=True)
    for var in relevant_vars:
        val = os.getenv(var)
        status = val if val is not None else "[NOT SET]"
        print(f"{var:<25}: {status}")

    print("\n--- Effective CLI Defaults ---")
    data_dir = os.getenv("DATA_DIR", "data")
    print(f"Effective Data Dir       : {(project_dir / data_dir).absolute()}")
    print("-" * 34)

def main():
    if sys.platform != "darwin":
        print("The daemon management script is only supported on macOS.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Manage the mesura-all macOS LaunchDaemon.")
    parser.add_argument("--install", action="store_true", help="Install and start the LaunchDaemon")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall and remove the LaunchDaemon")
    parser.add_argument("--unload", action="store_true", help="Temporarily stop (unload) the LaunchDaemon")
    parser.add_argument("--start", action="store_true", help="Start (load) the LaunchDaemon if it was unloaded")
    parser.add_argument("--check", action="store_true", help="Check if the LaunchDaemon is running")
    parser.add_argument("--logs", action="store_true", help="Tail the last 20 lines of daemon logs")
    parser.add_argument("--env-check", action="store_true", help="Troubleshoot environment variables and .env configuration")
    parser.add_argument("--uvx", action="store_true", help="Configure the daemon to explicitly run via 'uvx dvm-mesura' instead of a hardcoded path. Crucial if installing from an ephemeral uvx environment.")
    
    args = parser.parse_args()
    
    if args.install:
        do_install(use_uvx=args.uvx)
    elif args.uninstall:
        do_uninstall()
    elif args.unload:
        do_unload()
    elif args.start:
        do_start()
    elif args.check:
        do_check()
    elif args.logs:
        do_logs()
    elif args.env_check:
        do_env_check()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
