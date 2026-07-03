#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

# Ensure venv + deno binaries are available in PATH (pikaraoke, yt-dlp, deno)
HOME = Path.home()
VENV_BIN = HOME / ".venv-pikaraoke" / "bin"
DENO_BIN = HOME / ".deno" / "bin"

base_path = os.environ.get("PATH", "")
os.environ["PATH"] = f"{VENV_BIN}:{DENO_BIN}:/usr/local/bin:/usr/bin:/bin:{base_path}"


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

CHECK_INTERVAL = 5
INITIAL_WAIT = 10
EXTENDED_WAIT = 30


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
    logfile = HOME / "pikaraoke_output.log"
    with open(logfile, "a") as log:
        log.write(
            f"🎤 [LOG] Launching PiKaraoke @ {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        if not (VENV_BIN / "yt-dlp").exists():
            log.write("⚠️ [LOG] yt-dlp not found in venv bin\n")
        if not (DENO_BIN / "deno").exists():
            log.write("⚠️ [LOG] deno not found in ~/.deno/bin\n")
        try:
            subprocess.Popen(
                [str(VENV_BIN / "pikaraoke")],
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
            )
        except Exception as e:
            log.write(f"❌ [LOG] Failed to launch PiKaraoke: {e}\n")


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


def update_pikaraoke(target_version):
    """Upgrade pikaraoke and yt-dlp in the venv."""
    logfile = HOME / "pikaraoke_output.log"
    with open(logfile, "a") as log:
        log.write(
            f"🔄 [LOG] Upgrading pikaraoke to {target_version} + yt-dlp @ {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )

    # Dynamically inject the fetched target_version
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
    )
    if result.returncode != 0:
        log.write("⚠️ [LOG] pip upgrade exited with non-zero status\n")
    else:
        log.write("✅ [LOG] pip upgrade completed\n")


def check_and_update():
    """Fetch the latest version from PyPI and upgrade if local version is outdated."""
    installed = get_installed_pikaraoke_version()
    latest = get_latest_pikaraoke_version()

    # If PyPI is down or unreachable, gracefully skip updating and launch anyway
    if latest is None:
        print("⚠️ Unable to fetch latest version from PyPI. Skipping update check.")
        return False

    if installed < latest:
        show_info(
            f"🔄 Updating pikaraoke {installed} → {latest}\nUpdating before launch...",
            duration=2,
        )
        update_pikaraoke(latest)  # Pass the target version down
        return True

    return False


def main():
    # Quiet polling (INITIAL_WAIT)
    start = time.time()
    while time.time() - start < INITIAL_WAIT:
        if check_internet():
            check_and_update()
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
            check_and_update()
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Fallback if still offline — do not launch
    show_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
