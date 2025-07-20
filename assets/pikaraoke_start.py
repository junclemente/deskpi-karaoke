#!/usr/bin/env python3

import subprocess
import time
import socket
import os
from pathlib import Path
import tkinter as tk
import threading

CHECK_INTERVAL = 5
MAX_WAIT = 30


# --- Tkinter Popup Functions ---
def show_info_popup(message, title="PiKaraoke", duration=3, x=400, y=200):
    def popup():
        try:
            root = tk.Tk()
            root.title(title)
            root.geometry(f"+{x}+{y}")
            root.attributes("-topmost", True)
            root.resizable(False, False)
            tk.Label(root, text=message, padx=20, pady=20, font=("Arial", 12)).pack()
            root.after(duration * 1000, root.destroy)
            root.mainloop()
        except Exception as e:
            print(f"[INFO] {message} (GUI error: {e})")

    threading.Thread(target=popup).start()


def show_error_popup(message, title="PiKaraoke Error", x=400, y=200):
    def popup():
        try:
            root = tk.Tk()
            root.title(title)
            root.geometry(f"+{x}+{y}")
            root.attributes("-topmost", True)
            root.resizable(False, False)
            tk.Label(
                root, text=message, padx=20, pady=20, font=("Arial", 12), fg="red"
            ).pack()
            root.mainloop()
        except Exception as e:
            print(f"[ERROR] {message} (GUI error: {e})")

    threading.Thread(target=popup).start()


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
    show_info_popup("🔔 Connecting to internet...\nSearching for up to 30 seconds...")
    time.sleep(3)

    start_time = time.time()
    while (time.time() - start_time) < MAX_WAIT:
        if check_internet():
            show_info_popup(
                "✅ Internet connected.\nLaunching PiKaraoke...", duration=2
            )
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    show_error_popup(
        "❌ No internet found.\nPlease connect to the internet and try again."
    )


if __name__ == "__main__":
    main()
