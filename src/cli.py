"""Orchestrates the installer steps in order."""

import sys

from src.assets import copy_assets
from src.constants import DESKTOP_FILE_PATH, STATE_DIR, VENV_DIR
from src.network import install_deno, install_ytdlp_config
from src.shell import print_h
from src.state import record_state
from src.system import apt_install, check_platform, ensure_python_version
from src.venv import ensure_venv


def main():
    print_h("PiKaraoke Installer (dev)")
    ensure_python_version()
    check_platform()
    apt_install()
    install_deno()
    ensure_venv()
    install_ytdlp_config()
    copy_assets()
    record_state()

    print_h("All done")
    print("• Venv       :", VENV_DIR)
    print("• Autostart  :", DESKTOP_FILE_PATH)
    print("• State dir  :", STATE_DIR)
    print(
        "\nYou may need to log out and back in (or reboot) for autostart changes to take effect."
    )


def run():
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except SystemExit:
        raise
    except Exception as e:
        print(f"❌ Installer failed: {e}")
        sys.exit(1)
