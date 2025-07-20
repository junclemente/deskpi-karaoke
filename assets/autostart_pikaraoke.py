#!/usr/bin/env python3

import subprocess
import time
import socket
import os

from pathlib import Path

from pikaraoke_ui import show_error, show_info

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


def main():
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
