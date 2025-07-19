#!/usr/bin/env python3

import os
import platform
import subprocess
import shutil
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
    return "raspberrypi" in platform.uname().node.lower()


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
    print("🎬 Copying start script from assets...")
    src = Path(__file__).parent / "assets" / "pikaraoke_start.py"
    dst = Path.home() / "pikaraoke_start.py"
    shutil.copy(src, dst)
    dst.chmod(0o755)




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
    install_autostart_entry()

    print(
        "\n✅ Installation complete! You can launch PiKaraoke from the desktop or by running:"
    )
    print("   python3 ~/pikaraoke_start.py\n")


def install_autostart_entry():
    print("🔁 Copying autostart entry from assets...")
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)

    src = Path(__file__).parent / "assets" / "pikaraoke.desktop"
    dst = autostart_dir / "pikaraoke.desktop"
    shutil.copy(src, dst)
    dst.chmod(0o755)

    print(f"✅ Autostart file created at: {dst}")



if __name__ == "__main__":
    main()
