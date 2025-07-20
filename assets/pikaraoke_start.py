#!/usr/bin/env python3

import subprocess
import time
import socket
import os

from pathlib import Path

from assets.pikaraoke_ui import show_error, show_info

CHECK_INTERVAL = 5
MAX_WAIT = 30


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
    show_info("🔔 Connecting to internet...\nSearching for up to 30 seconds...")
    time.sleep(3)

    start_time = time.time()
    while (time.time() - start_time) < MAX_WAIT:
        if check_internet():
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    show_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
