#!/usr/bin/env python3

import subprocess
import time
import socket

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


def main():
    zenity_info("🔔 Connecting to internet...\nSearching for 30 seconds...")

    waited = 0
    while waited < MAX_WAIT:
        if check_internet():
            zenity_blocking_info(
                "✅ Internet connected.\nLaunching PiKaraoke...", timeout=2
            )
            subprocess.run(
                [
                    "lxterminal",
                    "-e",
                    "bash",
                    "-c",
                    "source /home/pi/.venv/bin/activate && pikaraoke",
                ]
            )
            return
        time.sleep(CHECK_INTERVAL)
        waited += CHECK_INTERVAL

    zenity_error("❌ No internet found.\nPlease connect to the internet and try again.")


if __name__ == "__main__":
    main()
