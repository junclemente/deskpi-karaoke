"""Optional DeskPi Lite 4 case driver installation (--deskpi)."""

import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

from src.shell import log_section, run

logger = logging.getLogger(__name__)

DESKPI_REPO_URL = "https://github.com/DeskPi-Team/deskpi_v1.git"


def _is_pi4() -> bool:
    try:
        model = Path("/proc/device-tree/model").read_text()
    except Exception:
        model = ""
    return "Raspberry Pi 4" in model


def _already_installed() -> bool:
    if Path("/usr/lib/deskpi").exists():
        return True
    return (
        subprocess.run(
            ["systemctl", "is-enabled", "deskpi.service"], capture_output=True
        ).returncode
        == 0
    )


def install_deskpi_drivers() -> bool:
    """Install DeskPi Lite 4 case drivers.

    Returns True if freshly installed (a reboot may be required); False if
    skipped (wrong hardware, already installed) or on failure.
    """
    log_section("Installing DeskPi Lite 4 drivers")

    if not _is_pi4():
        logger.warning("⚠️  --deskpi is for Pi 4 only. Skipping DeskPi driver install.")
        return False

    if _already_installed():
        logger.info("✅ DeskPi drivers already installed, skipping")
        return False

    clone_dir = Path(tempfile.mkdtemp(prefix="deskpi_v1_"))
    try:
        run(["git", "clone", DESKPI_REPO_URL, str(clone_dir)], check=False)
        run(f"sudo bash {clone_dir}/install.sh", check=False)
    finally:
        shutil.rmtree(clone_dir, ignore_errors=True)

    return True
