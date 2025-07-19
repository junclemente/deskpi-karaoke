#!/usr/bin/env python3

import subprocess
import time
import socket
import os
from pathlib import Path

CHECK_INTERVAL = 5
MAX_WAIT = 30


def zenity_info(message, timeout=3):
    subprocess.Popen(
        [
            "zenity",
            "--info",
            "--timeout",
            str(timeout),
            "--title=PiKaraoke",
            "--text",
            message,
        ]
    )


def zenity_blocking_info(message, timeout=3):
    subprocess.run(
        [
            "zenity",
            "--info",
            "--timeout",
            str(timeout),
            "--title=PiKaraoke",
            "--text",
            message,
        ]
    )


def zenity_error(message):
    subprocess.run(["zenity", "--error", "--title=PiKaraoke", "--text", message])


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

    print("🎤 PiKaraoke launched.")


def main():
    # zenity_info("🔔 Connecting to internet...\nSearching for 30 seconds...")

    # waited = 0
    # while waited < MAX_WAIT:
    #     if check_internet():
    #         zenity_blocking_info(
    #             "✅ Internet connected.\nLaunching PiKaraoke...", timeout=2
    #         )
    #         launch_pikaraoke()
    #         return
    #     time.sleep(CHECK_INTERVAL)
    #     waited += CHECK_INTERVAL

    # zenity_error("❌ No internet found.\nPlease connect to the internet and try again.")
    zenity_info("🔔 Connecting to internet...\nSearching for up to 30 seconds...")

    start_time = time.time()
    while (time.time() - start_time) < MAX_WAIT:
        if check_internet():
            zenity_blocking_info("✅ Internet connected.\nLaunching PiKaraoke...", timeout=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    zenity_error("❌ No internet found.\nPlease connect to the internet and try again.")



if __name__ == "__main__":
    main()
