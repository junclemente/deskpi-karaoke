#!/usr/bin/env python3

import argparse
import logging
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src import constants  # noqa: E402
from src.assets import remove_rc_block  # noqa: E402
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
    safe_remove(constants.VENV_DIR)


def remove_start_script():
    logger.info("🔍 Removing legacy start script...")
    safe_remove(constants.HOME / "pikaraoke_start.py")


def remove_copied_assets():
    logger.info("🔍 Removing copied installer assets...")
    safe_remove(constants.AUTOSTART_SCRIPT_PATH)
    safe_remove(constants.PIKARAOKE_UI_PATH)
    safe_remove(constants.STATE_TOML_HELPER_PATH)
    safe_remove(constants.ICON_PATH)


def remove_shortcut():
    logger.info("🔍 Removing desktop shortcut...")
    safe_remove(constants.DESKTOP_SHORTCUT_PATH)


def remove_logs():
    logger.info("🔍 Removing logs...")
    home = constants.HOME
    safe_remove(home / "pikaraoke_output.log")
    safe_remove(home / "pikaraoke_install.log")
    safe_remove(home / "pikaraoke_launcher.log")


def remove_autostart():
    logger.info("🔍 Removing autostart config...")
    safe_remove(constants.DESKTOP_FILE_PATH)


def remove_logrotate_config():
    logger.info("🔍 Removing logrotate config...")
    subprocess.run(["sudo", "rm", "-f", "/etc/logrotate.d/pikaraoke"], check=False)


def remove_pk_aliases():
    logger.info("🔍 Removing pk aliases...")
    safe_remove(constants.PK_ALIASES_PATH)
    remove_rc_block(constants.HOME / ".bashrc")
    remove_rc_block(constants.HOME / ".zshrc")


def remove_state_dir():
    logger.info("🔍 Removing installer state...")
    safe_remove(constants.STATE_DIR)


def remove_ytdlp_config():
    logger.info("🔍 Removing yt-dlp config...")
    safe_remove(constants.YTDLP_CONFIG_DIR)


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
    remove_copied_assets()
    remove_shortcut()
    remove_logs()
    remove_autostart()
    remove_logrotate_config()
    remove_pk_aliases()
    remove_state_dir()
    remove_ytdlp_config()

    if args.deskpi:
        remove_deskpi_drivers()
    else:
        logger.info("💡 DeskPi drivers preserved (use --deskpi to remove)")

    logger.info("\n✅ PiKaraoke has been uninstalled. Your songs are safe 🎵\n")


if __name__ == "__main__":
    main()
