"""Platform checks and system (apt) package installation."""

import platform
import shutil
import sys

from src.constants import APT_PKGS, PY_MIN
from src.shell import print_h, run


def ensure_python_version():
    if sys.version_info < PY_MIN:
        raise SystemExit(
            f"❌ Python {PY_MIN[0]}.{PY_MIN[1]}+ required. Found {sys.version.split()[0]}"
        )


def check_platform():
    # Soft checks for Pi + Bookworm Desktop
    print_h("Checking platform")
    uname = platform.uname()
    try:
        with open("/etc/os-release") as f:
            osrel = f.read().lower()
    except Exception:
        osrel = ""
    print(f"System : {uname.system} {uname.release} ({uname.machine})")
    if "bookworm" not in osrel:
        print("⚠️  Non-Bookworm OS detected. Proceeding anyway...")
    if "raspberry" not in (uname.machine.lower() + " " + osrel):
        print("ℹ️  This does not appear to be a Raspberry Pi. Proceeding anyway...")


def apt_install():
    print_h("Installing system packages (apt)")
    apt = shutil.which("apt-get") or shutil.which("apt")
    sudo = shutil.which("sudo")
    if not apt:
        print("ℹ️  apt not found (non-Debian system?) Skipping system packages.")
        return
    # Update
    cmd_update = f"{apt} update"
    # Install base pkgs
    pkgs = " ".join(APT_PKGS)
    cmd_install = f"{apt} install -y {pkgs}"
    # Chromium name varies (chromium vs chromium-browser) — try best-effort
    try_chromium = (
        f"{apt} install -y chromium || {apt} install -y chromium-browser || true"
    )
    try:
        if sudo:
            run(f"{sudo} {cmd_update}", check=False)
            run(f"{sudo} {cmd_install}", check=False)
            run(f"{sudo} {try_chromium}", check=False)
        else:
            run(cmd_update, check=False)
            run(cmd_install, check=False)
            run(try_chromium, check=False)
    except Exception as e:
        print(f"⚠️  apt install step had issues: {e}. Continuing...")
