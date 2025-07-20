#!/usr/bin/env python3

import argparse
import platform
import shutil
import site
import subprocess
import sys

from pathlib import Path

# --- Check Python Version ---
if sys.version_info < (3, 9):
    print("❌ Python 3.9+ is required to install PiKaraoke.")
    print(f"Detected version: {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)


# --- Parse CLI Arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Install PiKaraoke on Raspberry Pi 4..."
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
    # Attempt to get the latest git tag as the version of the installer project
    try:
        return (
            subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],  # Only the last tag
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
            .lstrip("v")
        )
    except Exception:
        return "0.0.0"


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
            "python3-pip",
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
    run_command([str(pip), "install", "--upgrade", "packaging"])
    run_command([str(pip), "install", "pikaraoke"])


def install_start_script():
    print("🎬 Copying start script from assets...")
    src = Path(__file__).parent / "assets" / "autostart_pikaraoke.py"
    dst = Path.home() / "autostart_pikaraoke.py"
    shutil.copy(src, dst)
    dst.chmod(0o755)


def install_ui_module():
    print("📁 Copying PiKaraoke UI module...")
    src = Path(__file__).parent / "assets" / "pikaraoke_ui.py"
    dst = Path.home() / "pikaraoke_ui.py"
    shutil.copy(src, dst)
    dst.chmod(0o644)
    print(f"✅ UI module installed at: {dst}")


# --- Main Entry Point ---
def main():
    args = parse_args()

    # Step 1: Set up the virtual environment early so packaging is available
    setup_virtualenv()

    # ✅ Now it's safe to import Version
    from packaging.version import Version

    version = get_version()
    print(f"\n🎤 PiKaraoke Installer v{version} Starting...\n")

    # Step 2: Clean uninstall if upgrading from older versions
    if Version(version) < Version("0.3.1"):
        print("🧹 Detected install < 0.3.1 — running uninstall_clean.py...")
        subprocess.run(["python3", "uninstall_clean.py"], check=True)

    # Step 3: Check for autoupdate flag
    update_flag = Path.home() / ".pikaraoke_update_pending"
    if update_flag.exists():
        print("🔔 Update flag detected - upgrading PiKaraoke...")
        update_flag.unlink()
        venv_bin = Path.home() / ".venv-pikaraoke" / "bin"
        pip = venv_bin / "pip"
        run_command([str(pip), "install", "--force-reinstall", "pikaraoke"])

    # Step 4: OS check & system package install
    check_platform()
    install_system_packages()

    # Step 5: Optional DeskPi drivers
    if args.deskpi:
        install_deskpi_drivers()
    else:
        print("💡 DeskPi driver install skipped (use --deskpi to enable)")

    # Step 6: Final setup steps
    install_start_script()
    install_autostart_entry()
    install_ui_module()

    print("\n✅ Installation complete! System will automatically reboot.")
    print("🔄 Rebooting...")
    subprocess.run(["sudo", "reboot"])


def install_autostart_entry():
    print("🔁 Copying autostart entry from assets...")
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)

    src = Path(__file__).parent / "assets" / "autostart_pikaraoke.desktop"
    dst = autostart_dir / "pikaraoke.desktop"
    shutil.copy(src, dst)
    dst.chmod(0o755)

    print(f"✅ Autostart file created at: {dst}")


if __name__ == "__main__":
    main()
