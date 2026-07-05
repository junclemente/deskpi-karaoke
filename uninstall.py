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
        description="Uninstall PiKaraoke (v0.3.0+) cleanly without touching songs"
    )
    parser.add_argument(
        "--deskpi",
        action="store_true",
        help="Also remove DeskPi Lite 4 drivers",
    )
    return parser.parse_args()


# --- Removal Tasks ---
def remove_current_virtualenv():
    logger.info("🔍 Removing current virtual environment...")
    safe_remove(Path.home() / ".venv-pikaraoke")


def remove_start_script():
    logger.info("🔍 Removing start script...")
    safe_remove(Path.home() / "pikaraoke_start.py")


def remove_shortcut():
    logger.info("🔍 Removing desktop shortcut...")
    safe_remove(Path.home() / "Desktop" / "Start PiKaraoke.desktop")


def remove_logs():
    logger.info("🔍 Removing logs...")
    home = Path.home()
    safe_remove(home / "pikaraoke_output.log")
    safe_remove(home / "pikaraoke_install.log")
    safe_remove(home / "pikaraoke_launcher.log")


def remove_autostart():
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


# --- Main Entry Point ---
def main():
    setup_logging()
    args = parse_args()
    logger.info("\n🧹 PiKaraoke Uninstaller (v0.3.0+) Starting...\n")

    remove_current_virtualenv()
    remove_start_script()
    remove_shortcut()
    remove_logs()
    remove_autostart()
    remove_logrotate_config()

    if args.deskpi:
        remove_deskpi_drivers()
    else:
        logger.info("💡 DeskPi drivers preserved (use --deskpi to remove)")

    logger.info("\n✅ PiKaraoke has been uninstalled. Your songs are safe 🎵\n")


if __name__ == "__main__":
    main()
