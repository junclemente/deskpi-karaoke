#!/usr/bin/env python3
import json
import logging
import os
import socket
import subprocess
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Ensure venv + deno binaries are available in PATH (pikaraoke, yt-dlp, deno).
# SHIM_BIN goes first so pikaraoke's "chromium-browser" lookup finds the
# installer's X11 shim (see assets/chromium-browser) before /usr/bin's.
HOME = Path.home()
SHIM_BIN = HOME / ".deskpi-karaoke" / "bin"
VENV_BIN = HOME / ".venv-pikaraoke" / "bin"
DENO_BIN = HOME / ".deno" / "bin"

base_path = os.environ.get("PATH", "")
os.environ["PATH"] = (
    f"{SHIM_BIN}:{VENV_BIN}:{DENO_BIN}:/usr/local/bin:/usr/bin:/bin:{base_path}"
)

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
from state_toml import load_state, save_state

CHECK_INTERVAL = 5
INITIAL_WAIT = 10
EXTENDED_WAIT = 30
UPDATE_TIMEOUT = 180

# Throttle PyPI polling per package — a kiosk device reboots far more often
# than either package cuts a new release, so there's no need to hit PyPI on
# every single boot.
VERSION_CHECK_INTERVAL = 6 * 60 * 60

STATE_FILE = HOME / ".deskpi-karaoke" / "state.toml"

# name -> where its installed/last-checked info lives in state.toml, and
# where to ask PyPI for its latest release
PACKAGES = {
    "pikaraoke": {
        "version_key": "pikaraoke_version",
        "checked_key": "pikaraoke_checked_at",
        "pypi_url": "https://pypi.org/pypi/pikaraoke/json",
    },
    "yt-dlp": {
        "version_key": "ytdlp_version",
        "checked_key": "ytdlp_checked_at",
        "pypi_url": "https://pypi.org/pypi/yt-dlp/json",
    },
}


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


def get_installed_version(package):
    try:
        out = subprocess.check_output(
            [str(VENV_BIN / "pip"), "show", package], text=True
        )
        for line in out.splitlines():
            if line.startswith("Version:"):
                return Version(line.split(":", 1)[1].strip())
    except Exception:
        pass
    return Version("0.0.0")


def get_latest_version(pypi_url, timeout=5):
    try:
        with urllib.request.urlopen(pypi_url, timeout=timeout) as r:
            data = json.load(r)
            return Version(data["info"]["version"])
    except Exception:
        return None


def update_package(package, target_version):
    logger.info(
        "🔄 Upgrading %s to %s @ %s",
        package,
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
                    f"{package}=={target_version}",
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
                timeout=UPDATE_TIMEOUT,
            )
            if result.returncode != 0:
                logger.warning("⚠️ %s pip upgrade exited with non-zero status", package)
            else:
                logger.info("✅ %s pip upgrade completed", package)
        except subprocess.TimeoutExpired:
            logger.error(
                "❌ %s pip upgrade timed out after %ss", package, UPDATE_TIMEOUT
            )


def _due_for_pypi_check(state, checked_key):
    try:
        last_checked = float(state.get(checked_key, 0))
    except (TypeError, ValueError):
        last_checked = 0.0
    return time.time() - last_checked >= VERSION_CHECK_INTERVAL


def check_and_update_all():
    """Check pikaraoke and yt-dlp for updates and upgrade whichever is outdated.

    Latest-version lookups hit PyPI, so each package's is throttled to once
    per VERSION_CHECK_INTERVAL (tracked via state.toml's *_checked_at keys),
    and when more than one package is actually due, their PyPI requests run
    concurrently rather than back-to-back.
    """
    state = load_state(STATE_FILE)
    due = [
        name
        for name, spec in PACKAGES.items()
        if _due_for_pypi_check(state, spec["checked_key"])
    ]

    latest = {}
    if due:
        with ThreadPoolExecutor(max_workers=len(due)) as pool:
            futures = {
                name: pool.submit(get_latest_version, PACKAGES[name]["pypi_url"])
                for name in due
            }
            latest = {name: future.result() for name, future in futures.items()}

    updates = {}
    now = str(time.time())
    for name, spec in PACKAGES.items():
        installed = get_installed_version(name)

        if name in due:
            updates[spec["checked_key"]] = now
            target = latest[name]
            if target is None:
                logger.warning(
                    "⚠️ Unable to fetch latest %s version from PyPI. Skipping check.",
                    name,
                )
            elif installed < target:
                show_info(
                    f"🔄 Updating {name} {installed} → {target}\n"
                    "Updating before launch...",
                    duration=2,
                )
                update_package(name, target)
                installed = get_installed_version(name)  # re-check actual result

        updates[spec["version_key"]] = str(installed)

    try:
        save_state(STATE_FILE, updates)
    except Exception:
        pass


def safe_check_and_update_all():
    """Run check_and_update_all() without letting any failure block the launch below."""
    try:
        check_and_update_all()
    except Exception as e:
        logger.error("❌ check_and_update_all() failed: %s", e)


def main():
    # Quiet polling (INITIAL_WAIT)
    start = time.time()
    while time.time() - start < INITIAL_WAIT:
        if check_internet():
            safe_check_and_update_all()
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
            safe_check_and_update_all()
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Fallback if still offline — do not launch
    show_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
