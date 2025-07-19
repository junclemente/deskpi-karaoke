#!/usr/bin/env python3

import subprocess


def main():
    subprocess.run(
        [
            "zenity",
            "--timeout=2",
            "--info",
            "--title=PiKaraoke",
            "--text=🎤 Launching PiKaraoke...",
        ]
    )

    bash_cmd = "source /home/pi/.venv/bin/activate && pikaraoke"
    subprocess.run(["lxterminal", "-e", "bash", "-c", bash_cmd])


if __name__ == "__main__":
    main()
