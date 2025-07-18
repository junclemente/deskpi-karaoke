#!/usr/bin/env python3

import subprocess
import os
import time
from pathlib import Path
import socket

TIMEOUT = 30


def wait_for_internet(timeout=TIMEOUT):
    print("🌐 Waiting for internet connection...")
    start = time.time()
    while time.time() - start < timeout:
        try:
            socket.gethostbyname("google.com")
            print("✅ Internet connection established.")
            return True
        except socket.gaierror:
            time.sleep(5)
    print("⚠️  No internet connection detected after timeout.")
    return False


def launch_pikaraoke():
    venv_bin = Path.home() / ".venv-pikaraoke" / "bin"
    env = os.environ.copy()
    env["PATH"] = f"{venv_bin}:{env['PATH']}"

    logfile = Path.home() / "pikaraoke_output.log"
    with open(logfile, "a") as log:
        subprocess.Popen(["pikaraoke"], stdout=log, stderr=log, env=env)

    print("🎤 PiKaraoke launched.")


def main():
    if wait_for_internet():
        launch_pikaraoke()
    else:
        print("❌ PiKaraoke not started due to lack of internet.")


if __name__ == "__main__":
    main()
