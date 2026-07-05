#!/usr/bin/env python3

import argparse
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.logging_config import setup_logging  # noqa: E402
from src.shell import safe_remove, stop_service  # noqa: E402

logger = logging.getLogger(__name__)


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
    logger.info("🔍 Removing virtual environments...")
    safe_remove(Path.home() / ".venv")
    safe_remove(Path.home() / ".venv-pikaraoke")


def remove_shortcuts_and_scripts():
    logger.info("🔍 Removing desktop shortcuts and scripts...")
    home = Path.home()
    safe_remove(home / "Desktop" / "Start PiKaraoke.desktop")
    safe_remove(home / "pikaraoke_start_script.sh")
    safe_remove(home / "pikaraoke_launcher.sh")
    safe_remove(home / "pikaraoke_start.py")


def remove_logs():
    logger.info("🔍 Removing logs...")
    home = Path.home()
    safe_remove(home / "pikaraoke_output.log")
    safe_remove(home / "pikaraoke_install.log")
    safe_remove(home / "pikaraoke_launcher.log")


def remove_autostart_config():
    logger.info("🔍 Removing autostart config...")
    safe_remove(Path("/etc/xdg/autostart/pikaraoke.desktop"))


def remove_logrotate_config():
    logger.info("🔍 Removing logrotate config...")
    subprocess.run(["sudo", "rm", "-f", "/etc/logrotate.d/pikaraoke"], check=False)


def remove_deskpi_drivers():
    logger.info("🧹 Removing DeskPi Lite drivers...")
    stop_service("deskpi.service")
    subprocess.run(
        ["sudo", "rm", "-f", "/etc/systemd/system/deskpi.service"], check=False
    )
    subprocess.run(["sudo", "rm", "-rf", "/usr/lib/deskpi*"], check=False)
    subprocess.run(["sudo", "rm", "-f", "/etc/deskpi.conf"], check=False)


def remove_legacy_install_folder():
    logger.info("🔍 Checking legacy folder: ~/pikaraoke")
    pikaraoke_dir = Path.home() / "pikaraoke"
    if pikaraoke_dir.exists():
        if "pikaraoke-songs" in [p.name.lower() for p in pikaraoke_dir.iterdir()]:
            logger.warning(
                "🚫 Skipping legacy folder (contains 'pikaraoke-songs'): %s",
                pikaraoke_dir,
            )
        else:
            safe_remove(pikaraoke_dir)


# --- Main Entry Point ---
def main():
    setup_logging()
    args = parse_args()
    logger.info("\n🧼 PiKaraoke Legacy Clean Uninstaller Starting...\n")

    remove_virtualenvs()
    remove_shortcuts_and_scripts()
    remove_logs()
    remove_autostart_config()
    remove_logrotate_config()
    remove_legacy_install_folder()

    if args.deskpi:
        remove_deskpi_drivers()
    else:
        logger.info("💡 DeskPi drivers preserved (use --deskpi to remove)")

    logger.info("\n✅ Cleanup complete. Your songs are safe 🎵\n")


if __name__ == "__main__":
    main()
