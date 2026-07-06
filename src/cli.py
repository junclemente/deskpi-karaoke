"""Orchestrates the installer steps in order."""

import argparse
import logging
import sys

from src import constants
from src.assets import copy_assets
from src.deskpi import install_deskpi_drivers
from src.logging_config import setup_logging
from src.logs import install_logrotate_config
from src.network import install_deno, install_ytdlp_config
from src.shell import log_section
from src.state import record_state, save_state
from src.system import apt_install, check_platform, ensure_python_version
from src.venv import ensure_venv

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="PiKaraoke installer")
    parser.add_argument(
        "--deskpi",
        action="store_true",
        help="Also install DeskPi Lite 4 case drivers (Pi 4 only)",
    )
    return parser.parse_args()


def main(args):
    log_section("PiKaraoke Installer (dev)")
    ensure_python_version()
    check_platform()
    apt_install()
    install_deno()
    ensure_venv()
    install_ytdlp_config()
    install_logrotate_config()
    copy_assets()

    if args.deskpi:
        reboot_required = install_deskpi_drivers()
        save_state({"reboot_required": reboot_required})

    record_state()

    log_section("All done")
    logger.info("• Venv       : %s", constants.VENV_DIR)
    logger.info("• Autostart  : %s", constants.DESKTOP_FILE_PATH)
    logger.info("• Desktop icon: %s", constants.DESKTOP_SHORTCUT_PATH)
    logger.info("• State dir  : %s", constants.STATE_DIR)
    logger.info(
        "\nYou may need to log out and back in (or reboot) for autostart "
        "changes to take effect."
    )


def run():
    setup_logging()
    args = parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        logger.info("\nInterrupted.")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as e:
        logger.error("❌ Installer failed: %s", e)
        sys.exit(1)
