#!/usr/bin/env python3
import json
import logging
import os
import socket
import subprocess
import time
import urllib.request
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure venv + deno binaries are available in PATH (pikaraoke, yt-dlp, deno)
HOME = Path.home()
VENV_BIN = HOME / ".venv-pikaraoke" / "bin"
DENO_BIN = HOME / ".deno" / "bin"

base_path = os.environ.get("PATH", "")
os.environ["PATH"] = f"{VENV_BIN}:{DENO_BIN}:/usr/local/bin:/usr/bin:/bin:{base_path}"

# Two log files, two rotation mechanisms:
# - OUTPUT_LOG_FILE: the pikaraoke subprocess's own raw stdout/stderr, written
#   directly by that child process via an inherited fd — rotated externally
#   by system logrotate (see src/logs.py), since this script can't safely
#   rotate a file another process is writing into.
# - LAUNCHER_LOG_FILE: this script's own bookkeeping messages — only this
#   process writes here, so a plain RotatingFileHandler is safe.
OUTPUT_LOG_FILE = HOME / "pikaraoke_output.log"
LAUNCHER_LOG_FILE = HOME / "pikaraoke_launcher.log"

logger = logging.getLogger("pikaraoke_autostart")
logger.setLevel(logging.INFO)
_handler = RotatingFileHandler(LAUNCHER_LOG_FILE, maxBytes=2_000_000, backupCount=3)
_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(_handler)


try:
    from packaging.version import Version
except Exception:
    # Fallback if packaging isn't installed
    class Version(str):
        @property
        def major(self):
            return int(str(self).split(".")[0] or 0)

        @property
        def minor(self):
            return int((str(self).split(".") + ["0", "0"])[1] or 0)


from pikaraoke_ui import show_error, show_info
from state_toml import save_state

CHECK_INTERVAL = 5
INITIAL_WAIT = 10
EXTENDED_WAIT = 30
UPDATE_TIMEOUT = 180

STATE_FILE = HOME / ".deskpi-karaoke" / "state.toml"


def check_internet(timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.create_connection(("8.8.8.8", 53))
        return True
    except OSError:
        return False


def launch_pikaraoke():
    env = os.environ.copy()
    env["PATH"] = os.environ["PATH"]
    logger.info("🎤 Launching PiKaraoke @ %s", time.strftime("%Y-%m-%d %H:%M:%S"))
    if not (VENV_BIN / "yt-dlp").exists():
        logger.warning("⚠️ yt-dlp not found in venv bin")
    if not (DENO_BIN / "deno").exists():
        logger.warning("⚠️ deno not found in ~/.deno/bin")
    try:
        with open(OUTPUT_LOG_FILE, "a") as log:
            subprocess.Popen(
                [str(VENV_BIN / "pikaraoke")],
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
            )
    except Exception as e:
        logger.error("❌ Failed to launch PiKaraoke: %s", e)


def get_installed_pikaraoke_version():
    try:
        out = subprocess.check_output(
            [str(VENV_BIN / "pip"), "show", "pikaraoke"], text=True
        )
        for line in out.splitlines():
            if line.startswith("Version:"):
                return Version(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return Version("0.0.0")


def get_latest_pikaraoke_version(timeout=5):
    url = "https://pypi.org/pypi/pikaraoke/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.load(r)
            return Version(data["info"]["version"])
    except Exception:
        return None


def store_pikaraoke_version(version):
    """Persist the currently-installed pikaraoke version, readable without a venv pip call."""
    try:
        save_state(STATE_FILE, {"pikaraoke_version": str(version)})
    except Exception:
        pass


def update_pikaraoke(target_version):
    """Upgrade pikaraoke and yt-dlp in the venv."""
    logger.info(
        "🔄 Upgrading pikaraoke to %s + yt-dlp @ %s",
        target_version,
        time.strftime("%Y-%m-%d %H:%M:%S"),
    )
    with open(OUTPUT_LOG_FILE, "a") as log:
        try:
            result = subprocess.run(
                [
                    str(VENV_BIN / "pip"),
                    "install",
                    "--upgrade",
                    f"pikaraoke=={target_version}",
                    "yt-dlp",
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=UPDATE_TIMEOUT,
            )
            if result.returncode != 0:
                logger.warning("⚠️ pip upgrade exited with non-zero status")
            else:
                logger.info("✅ pip upgrade completed")
        except subprocess.TimeoutExpired:
            logger.error("❌ pip upgrade timed out after %ss", UPDATE_TIMEOUT)


def check_and_update():
    """Fetch the latest version from PyPI and upgrade if local version is outdated."""
    installed = get_installed_pikaraoke_version()
    latest = get_latest_pikaraoke_version()

    # If PyPI is down or unreachable, gracefully skip updating and launch anyway
    if latest is None:
        logger.warning(
            "⚠️ Unable to fetch latest version from PyPI. Skipping update check."
        )
        store_pikaraoke_version(installed)
        return False

    if installed < latest:
        show_info(
            f"🔄 Updating pikaraoke {installed} → {latest}\nUpdating before launch...",
            duration=2,
        )
        update_pikaraoke(latest)  # Pass the target version down
        installed = get_installed_pikaraoke_version()  # re-check actual result
        store_pikaraoke_version(installed)
        return True

    store_pikaraoke_version(installed)
    return False


def safe_check_and_update():
    """Run check_and_update() without letting any failure block the launch below."""
    try:
        check_and_update()
    except Exception as e:
        logger.error("❌ check_and_update() failed: %s", e)


def main():
    # Quiet polling (INITIAL_WAIT)
    start = time.time()
    while time.time() - start < INITIAL_WAIT:
        if check_internet():
            safe_check_and_update()
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Extended wait with notification
    show_info(
        "🔔 Connecting to internet...\nSearching for up to 30 seconds...", duration=2
    )
    start = time.time()
    while time.time() - start < EXTENDED_WAIT:
        if check_internet():
            safe_check_and_update()
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Fallback if still offline — do not launch
    show_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
