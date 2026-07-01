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


def check_wlan0_internet(timeout=3):
    """Return True only if 8.8.8.8 is reachable via wlan0, ignoring eth0.

    Uses ping -I wlan0 so the kernel is forced to route through the WiFi
    interface regardless of what other interfaces are up.
    """
    try:
        result = subprocess.run(
            ["ping", "-I", "wlan0", "-c", "1", "-W", str(timeout), "8.8.8.8"],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0
    except Exception:
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


def update_pikaraoke():
    """Upgrade pikaraoke and yt-dlp in the venv. Runs synchronously before launch."""
    logfile = HOME / "pikaraoke_output.log"
    with open(logfile, "a") as log:
        log.write(
            f"🔄 [LOG] Upgrading pikaraoke + yt-dlp @ {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        result = subprocess.run(
            [str(VENV_BIN / "pip"), "install", "--upgrade", "pikaraoke==1.18.0", "yt-dlp"],
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        if result.returncode != 0:
            log.write("⚠️ [LOG] pip upgrade exited with non-zero status\n")
        else:
            log.write("✅ [LOG] pip upgrade completed\n")


def _find_splash_py():
    matches = sorted(
        (VENV_BIN.parent / "lib").glob(
            "python*/site-packages/pikaraoke/routes/splash.py"
        )
    )
    return matches[0] if matches else None


def patch_pikaraoke():
    """Patch pikaraoke splash.py to pass 'k.url' arg to get_raspi_wifi_text(). Idempotent."""
    logfile = HOME / "pikaraoke_output.log"
    target = "text = get_raspi_wifi_text(k.url)"
    wrong_patch = "text = get_raspi_wifi_text(url)"
    unpatched = "text = get_raspi_wifi_text()"
    with open(logfile, "a") as log:
        splash = _find_splash_py()
        if splash is None:
            log.write("⚠️ [PATCH] splash.py not found in venv — skipping\n")
            return
        text = splash.read_text(encoding="utf-8")
        if target in text:
            log.write(f"✅ [PATCH] {splash.name} already patched — no change needed\n")
            return
        if wrong_patch in text:
            splash.write_text(text.replace(wrong_patch, target, 1), encoding="utf-8")
            log.write(f"✅ [PATCH] Corrected wrong patch in {splash}\n")
            return
        if unpatched in text:
            splash.write_text(text.replace(unpatched, target, 1), encoding="utf-8")
            log.write(f"✅ [PATCH] Patched get_raspi_wifi_text() call in {splash}\n")
            return
        log.write(f"⚠️ [PATCH] No known pattern found in {splash} — skipping\n")


_PINNED_VERSION = Version("1.18.0")


def check_and_update():
    """Upgrade if installed pikaraoke is below the pinned version. Returns True if update ran."""
    installed = get_installed_pikaraoke_version()
    if installed < _PINNED_VERSION:
        show_info(
            f"🔄 Updating pikaraoke {installed} → {_PINNED_VERSION}\nUpdating before launch...",
            duration=2,
        )
        update_pikaraoke()
        patch_pikaraoke()
        return True
    return False


def main():
    # Quiet polling (INITIAL_WAIT)
    start = time.time()
    while time.time() - start < INITIAL_WAIT:
        if check_wlan0_internet():
            check_and_update()
            patch_pikaraoke()
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
        if check_wlan0_internet():
            check_and_update()
            patch_pikaraoke()
            show_info("✅ Internet connected.\nLaunching PiKaraoke...", duration=2)
            launch_pikaraoke()
            return
        time.sleep(CHECK_INTERVAL)

    # Fallback if still offline: launch the WiFi captive portal so the user
    # can enter their home WiFi credentials from any phone or laptop.
    try:
        from raspi_portal import run_portal
        run_portal()
    except Exception as exc:
        show_error(
            f"❌ No internet found.\nPortal error: {exc}\n"
            "Please connect to the internet and restart."
        )


if __name__ == "__main__":
    main()
