#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path
import argparse

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.shell import safe_remove, stop_service


# --- Parse CLI Arguments ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Clean uninstall of all PiKaraoke versions (legacy and current)"
    )
    parser.add_argument(
        "--deskpi",
        action="store_true",
        help="Also remove DeskPi Lite 4 drivers",
    )
    return parser.parse_args()


# --- Removal Tasks ---
def remove_virtualenvs():
    print("🔍 Removing virtual environments...")
    safe_remove(Path.home() / ".venv")
    safe_remove(Path.home() / ".venv-pikaraoke")


def remove_shortcuts_and_scripts():
    print("🔍 Removing desktop shortcuts and scripts...")
    home = Path.home()
    safe_remove(home / "Desktop" / "Start PiKaraoke.desktop")
    safe_remove(home / "pikaraoke_start_script.sh")
    safe_remove(home / "pikaraoke_launcher.sh")
    safe_remove(home / "pikaraoke_start.py")


def remove_logs():
    print("🔍 Removing logs...")
    home = Path.home()
    safe_remove(home / "pikaraoke_output.log")
    safe_remove(home / "pikaraoke_install.log")


def remove_autostart_config():
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


def remove_legacy_install_folder():
    print("🔍 Checking legacy folder: ~/pikaraoke")
    pikaraoke_dir = Path.home() / "pikaraoke"
    if pikaraoke_dir.exists():
        if "pikaraoke-songs" in [p.name.lower() for p in pikaraoke_dir.iterdir()]:
            print(
                f"🚫 Skipping legacy folder (contains 'pikaraoke-songs'): {pikaraoke_dir}"
            )
        else:
            safe_remove(pikaraoke_dir)


# --- Main Entry Point ---
def main():
    args = parse_args()
    print("\n🧼 PiKaraoke Legacy Clean Uninstaller Starting...\n")

    remove_virtualenvs()
    remove_shortcuts_and_scripts()
    remove_logs()
    remove_autostart_config()
    remove_legacy_install_folder()

    if args.deskpi:
        remove_deskpi_drivers()
    else:
        print("💡 DeskPi drivers preserved (use --deskpi to remove)")

    print("\n✅ Cleanup complete. Your songs are safe 🎵\n")


if __name__ == "__main__":
    main()
