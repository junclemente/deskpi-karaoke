#!/usr/bin/env python3

import subprocess
import time
import socket
import os

from pacakging.version import Version
from pikaraoke_ui import show_error, show_info
from pathlib import Path


CHECK_INTERVAL = 5
INITIAL_WAIT = 10
EXTENDED_WAIT = 30


# --- Logic ---
def check_internet():
    try:
        socket.setdefaulttimeout(3)
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
        log.write("🎤 [LOG] launch_pikaraoke() triggered\n")
        subprocess.Popen([str(venv_bin / "pikaraoke")], stdout=log, stderr=log, env=env)

def get_installed_pikaraoke_version():
    try:
        output = subprocess.check_output(["pikaraoke", "--version"])
        return Version(output.decode().strip().lstrip("v"))
    except Exception:
        return Version("0.0.0")
    
def get_latest_pikaraoke_version():
    try: 
        with urllib.request.urlopen("https://pypi.org/pypi/pikaraoke/json") as response: 
            data = json.load(response)
            return Version(data["info"]["version"])
    except Exception: 
        return None 

def mark_for_update():
    flag_path = Path.home() / ".pikaraoke_update_pending" 
    flag_path.touch()
    print("🔔 Update flag set. PiKaraoke will update on next launch.")


def main():
    # check for new major.minor version of PiKaraoke
    installed_version = get_installed_pikaraoke_version()
    latest_version = get_latest_pikaraoke_version()
    if (latest_version and (installed_version.major, installed_version.minor) < 
        (latest_version.major, latest_version.minor)):
        mark_for_update()

    # quiet polling - search for internet
    start_time = time.time()
    while (time.time() - start_time) < INITIAL_WAIT:
        if check_internet():
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # show popup if internet not found with INITIAL_WAIT period
    show_info(
        "🔔 Connecting to internet...\nSearching for up to 30 seconds...", duration=2
    )

    extended_start = time.time()
    while (time.time() - extended_start) < EXTENDED_WAIT:
        if check_internet():
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # fallback if internet not found
    show_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
