"""Platform checks and system (apt) package installation."""

import logging
import platform
import shutil
import sys

from src import constants
from src.shell import log_section, run

logger = logging.getLogger(__name__)


def ensure_python_version():
    if sys.version_info < constants.PY_MIN:
        raise SystemExit(
            f"❌ Python {constants.PY_MIN[0]}.{constants.PY_MIN[1]}+ required. "
            f"Found {sys.version.split()[0]}"
        )


def check_platform():
    # Soft checks for Pi + Bookworm Desktop
    log_section("Checking platform")
    uname = platform.uname()
    try:
        with open("/etc/os-release") as f:
            osrel = f.read().lower()
    except Exception:
        osrel = ""
    logger.info("System : %s %s (%s)", uname.system, uname.release, uname.machine)
    if "bookworm" not in osrel:
        logger.warning("⚠️  Non-Bookworm OS detected. Proceeding anyway...")
    if "raspberry" not in (uname.machine.lower() + " " + osrel):
        logger.info(
            "ℹ️  This does not appear to be a Raspberry Pi. Proceeding anyway..."
        )


def apt_install():
    log_section("Installing system packages (apt)")
    apt = shutil.which("apt-get") or shutil.which("apt")
    sudo = shutil.which("sudo")
    if not apt:
        logger.info("ℹ️  apt not found (non-Debian system?) Skipping system packages.")
        return
    # Update
    cmd_update = f"{apt} update"
    # Install base pkgs
    pkgs = " ".join(constants.APT_PKGS)
    cmd_install = f"{apt} install -y {pkgs}"
    # Chromium name varies (chromium vs chromium-browser) — try best-effort
    try_chromium = (
        f"{apt} install -y chromium || {apt} install -y chromium-browser || true"
    )
    try:
        if sudo:
            run(f"{sudo} {cmd_update}", check=False)
            run(f"{sudo} {cmd_install}", check=False)
            run(f"{sudo} {try_chromium}", check=False)
        else:
            run(cmd_update, check=False)
            run(cmd_install, check=False)
            run(try_chromium, check=False)
    except Exception as e:
        logger.warning("⚠️  apt install step had issues: %s. Continuing...", e)
