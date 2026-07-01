#!/usr/bin/env python3

import os
import shutil
import subprocess
from pathlib import Path
import argparse


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


_SONGS_DIR = Path.home() / "pikaraoke-songs"


# --- Utility Functions ---
def safe_remove(path: Path):
    """Removes a file or directory if it exists — never touches ~/pikaraoke-songs."""
    if not path.exists():
        return
    # Protect songs dir and anything inside it
    try:
        path.resolve().relative_to(_SONGS_DIR.resolve())
        print(f"🚫 Skipping (protected songs folder): {path}")
        return
    except ValueError:
        pass
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
    print("🔍 Removing autostart config and helper scripts...")
    home = Path.home()
    safe_remove(home / ".config" / "autostart" / "pikaraoke.desktop")
    safe_remove(home / "autostart_pikaraoke.py")
    safe_remove(home / "pikaraoke_ui.py")
    safe_remove(home / ".pk_aliases")
    safe_remove(home / ".deskpi-karaoke")


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

    songs_dir = Path.home() / "pikaraoke-songs"
    if songs_dir.exists():
        print(f"🎵 Songs folder will be preserved: {songs_dir}")

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
