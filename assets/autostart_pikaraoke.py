#!/usr/bin/env python3
import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

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
    venv_bin = Path.home() / ".venv-pikaraoke" / "bin"
    env = os.environ.copy()
    env["PATH"] = f"{venv_bin}:{env['PATH']}"
    logfile = Path.home() / "pikaraoke_output.log"
    with open(logfile, "a") as log:
        log.write(
            f"🎤 [LOG] Launching PiKaraoke @ {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        # Launch via entrypoint so we respect the installed package
        subprocess.Popen(["pikaraoke"], stdout=log, stderr=subprocess.STDOUT, env=env)


def get_installed_pikaraoke_version():
    try:
        out = subprocess.check_output(["pikaraoke", "--version"])
        return Version(out.decode().strip().lstrip("v"))
    except Exception:
        return Version("0.0.0")


def get_latest_pikaraoke_version(timeout=2):
    url = "https://pypi.org/pypi/pikaraoke/json"
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            data = json.load(r)
            return Version(data["info"]["version"])
    except Exception:
        return None


def mark_for_update():
    flag_path = Path.home() / ".pikaraoke_update_pending"
    flag_path.touch()
    print("🔔 Update flag set. PiKaraoke will update on next launch.")


def main():
    # Opportunistic package update hint (non-blocking)
    installed_version = get_installed_pikaraoke_version()
    latest_version = get_latest_pikaraoke_version()
    if latest_version and (installed_version.major, installed_version.minor) < (
        latest_version.major,
        latest_version.minor,
    ):
        mark_for_update()

    # Quiet polling (INITIAL_WAIT)
    start = time.time()
    while time.time() - start < INITIAL_WAIT:
        if check_internet():
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Extended wait with small hint
    show_info(
        "🔔 Connecting to internet...\nSearching for up to 30 seconds...", duration=2
    )
    start = time.time()
    while time.time() - start < EXTENDED_WAIT:
        if check_internet():
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Fallback if still offline
    show_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
