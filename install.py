#!/usr/bin/env python3

import os
import platform
import subprocess
from pathlib import Path
import argparse


# --- Parse CLI Arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Install PiKaraoke on Raspberry Pi 4 (v0.3.0)"
    )
    parser.add_argument(
        "--deskpi",
        action="store_true",
        help="Install DeskPi Lite 4 drivers",
    )
    return parser.parse_args()


# --- Utility Functions ---
def run_command(cmd, cwd=None):
    """Run a shell command and handle errors"""
    print(f"▶️  Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def is_raspberry_pi():
    return "raspberrypi" in platform.uname().nodename.lower()


def get_version():
    try:
        version_file = Path("VERSION")
        if version_file.exists():
            return version_file.read_text().strip()
    except Exception:
        pass
    return "unknown"


# --- Install Tasks ---
def check_platform():
    print("🧠 Checking platform...")
    if not is_raspberry_pi():
        print("⚠️  Not running on Raspberry Pi. Proceeding anyway...")

    os_release = Path("/etc/os-release").read_text()
    if "bookworm" not in os_release.lower():
        print("⚠️  Warning: You are not running Raspberry Pi OS Bookworm.")


def install_system_packages():
    print("📦 Installing system packages...")
    run_command(["sudo", "apt-get", "update"])
    run_command(
        [
            "sudo",
            "apt-get",
            "install",
            "-y",
            "ffmpeg",
            "chromium-browser",
            "chromium-chromedriver",
            "git",
            "python3-venv",
        ]
    )


def install_deskpi_drivers():
    print("🛠️ Installing DeskPi Lite 4 drivers...")
    run_command(["git", "clone", "https://github.com/DeskPi-Team/deskpi_v1.git"])
    run_command(["sudo", "./install.sh"], cwd="deskpi_v1")


def setup_virtualenv():
    print("🐍 Setting up virtual environment...")
    venv_path = Path.home() / ".venv-pikaraoke"
    if not venv_path.exists():
        run_command(["python3", "-m", "venv", str(venv_path)])
    pip = venv_path / "bin" / "pip"
    run_command([str(pip), "install", "--upgrade", "pip"])
    run_command([str(pip), "install", "pikaraoke"])


def install_start_script():
    print("🎬 Creating start script...")
    script_path = Path.home() / "pikaraoke_start.py"
    script_path.write_text(
        f"""#!/usr/bin/env python3

import subprocess
import os
from pathlib import Path

venv_bin = Path.home() / ".venv-pikaraoke" / "bin"
env = os.environ.copy()
env["PATH"] = f"{{venv_bin}}:{{env['PATH']}}"

logfile = Path.home() / "pikaraoke_output.log"
with open(logfile, "a") as log:
    subprocess.Popen(["pikaraoke"], stdout=log, stderr=log, env=env)

print("✅ PiKaraoke launched.")
"""
    )
    script_path.chmod(0o755)


def install_desktop_shortcut():
    print("🖥️ Creating desktop shortcut...")
    desktop_entry = Path.home() / "Desktop" / "Start PiKaraoke.desktop"
    desktop_entry.write_text(
        f"""[Desktop Entry]
Name=Start PiKaraoke
Comment=Launch PiKaraoke
Exec=lxterminal -e "python3 /home/pi/pikaraoke_start.py"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Audio;Application;
"""
    )
    desktop_entry.chmod(0o755)


# --- Main Entry Point ---
def main():
    args = parse_args()
    version = get_version()
    print(f"\n🎤 PiKaraoke Installer v{version} Starting...\n")

    check_platform()

    install_system_packages()

    if args.deskpi:
        install_deskpi_drivers()
    else:
        print("💡 DeskPi driver install skipped (use --deskpi to enable)")

    setup_virtualenv()
    install_start_script()
    install_desktop_shortcut()

    print(
        "\n✅ Installation complete! You can launch PiKaraoke from the desktop or by running:"
    )
    print("   python3 ~/pikaraoke_start.py\n")


if __name__ == "__main__":
    main()
