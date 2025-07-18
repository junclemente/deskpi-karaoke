#!/usr/bin/env python3

import os
import shutil
import subprocess
from pathlib import Path
import argparse


# --- Parse CLI Arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Uninstall PiKaraoke (v0.3.0+) cleanly without touching songs"
    )
    parser.add_argument(
        "--deskpi",
        action="store_true",
        help="Also remove DeskPi Lite 4 drivers",
    )
    return parser.parse_args()


# --- Utility Functions ---
def safe_remove(path: Path):
    """Removes a file or directory if it exists — skips if 'pikaraoke-songs' is in path"""
    if not path.exists():
        return

    if path.is_dir() and "pikaraoke-songs" in path.name.lower():
        print(f"🚫 Skipping songs folder: {path}")
        return

    try:
        if path.is_dir():
            shutil.rmtree(path)
            print(f"🗑️ Removed directory: {path}")
        else:
            path.unlink()
            print(f"🗑️ Removed file: {path}")
    except Exception as e:
        print(f"❌ Error removing {path}: {e}")


def stop_service(name):
    """Stops and disables a systemd service"""
    subprocess.run(["sudo", "systemctl", "stop", name], check=False)
    subprocess.run(["sudo", "systemctl", "disable", name], check=False)


# --- Removal Tasks ---
def remove_current_virtualenv():
    print("🔍 Removing current virtual environment...")
    safe_remove(Path.home() / ".venv-pikaraoke")


def remove_start_script():
    print("🔍 Removing start script...")
    safe_remove(Path.home() / "pikaraoke_start.py")


def remove_shortcut():
    print("🔍 Removing desktop shortcut...")
    safe_remove(Path.home() / "Desktop" / "Start PiKaraoke.desktop")


def remove_logs():
    print("🔍 Removing logs...")
    home = Path.home()
    safe_remove(home / "pikaraoke_output.log")
    safe_remove(home / "pikaraoke_install.log")


def remove_autostart():
    print("🔍 Removing autostart config...")
    safe_remove(Path("/etc/xdg/autostart/pikaraoke.desktop"))


def remove_deskpi_drivers():
    print("🧹 Removing DeskPi Lite drivers...")
    stop_service("deskpi.service")
    subprocess.run(
        ["sudo", "rm", "-f", "/etc/systemd/system/deskpi.service"], check=False
    )
    subprocess.run(["sudo", "rm", "-rf", "/usr/lib/deskpi*"], check=False)
    subprocess.run(["sudo", "rm", "-f", "/etc/deskpi.conf"], check=False)


# --- Main Entry Point ---
def main():
    args = parse_args()
    print("\n🧹 PiKaraoke Uninstaller (v0.3.0+) Starting...\n")

    remove_current_virtualenv()
    remove_start_script()
    remove_shortcut()
    remove_logs()
    remove_autostart()

    if args.deskpi:
        remove_deskpi_drivers()
    else:
        print("💡 DeskPi drivers preserved (use --deskpi to remove)")

    print("\n✅ PiKaraoke has been uninstalled. Your songs are safe 🎵\n")


if __name__ == "__main__":
    main()
