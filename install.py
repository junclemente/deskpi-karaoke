#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PiKaraoke Installer (dev branch)
- Idempotent
- Creates ~/.venv-pikaraoke
- Installs core packages (pikaraoke, packaging, yt-dlp)
- Copies autostart + UI helpers
- Installs pk_aliases and sources in shell rc files
- Records installer state under ~/.deskpi-karaoke
"""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

HOME = Path.home()
STATE_DIR = HOME / ".deskpi-karaoke"
VENV_DIR = HOME / ".venv-pikaraoke"
REPO_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = REPO_ROOT / "assets"
AUTOSTART_DIR = HOME / ".config" / "autostart"
DESKTOP_FILE_PATH = AUTOSTART_DIR / "pikaraoke.desktop"

PY_MIN = (3, 9)

PKG_CORE = [
    "pip>=24.0",
    "setuptools>=68",
    "wheel",
    "packaging>=24.0",
    "yt-dlp>=2024.7.0",
    "pikaraoke",  # main app
]

APT_PKGS = [
    "python3-venv",
    "python3-pip",
    "ffmpeg",
]


def print_h(msg: str):
    print(f"\n=== {msg} ===")


def run(cmd, check=True, cwd=None, env=None, capture_output=False, text=True):
    if isinstance(cmd, str):
        shell = True
        return subprocess.run(
            cmd,
            check=check,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=text,
            shell=True,
        )
    else:
        return subprocess.run(
            cmd, check=check, cwd=cwd, env=env, capture_output=capture_output, text=text
        )


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
    cmd_update = f"{apt} update -y"
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


def ensure_venv():
    print_h("Ensuring Python venv")
    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
    py = VENV_DIR / "bin" / "python"
    pip = [str(py), "-m", "pip"]
    run(pip + ["install", "--upgrade"] + PKG_CORE, check=False)
    return py


def copy_assets():
    print_h("Copying assets to $HOME")
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    # autostart script & UI
    shutil.copy2(ASSETS_DIR / "autostart_pikaraoke.py", HOME / "autostart_pikaraoke.py")
    shutil.copy2(ASSETS_DIR / "pikaraoke_ui.py", HOME / "pikaraoke_ui.py")
    # desktop entry (we regenerate Exec line to venv python)
    desktop_src = ASSETS_DIR / "autostart_pikaraoke.desktop"
    if desktop_src.exists():
        # Load existing, replace Exec= line
        content = desktop_src.read_text()
        exec_line = f"Exec={VENV_DIR}/bin/python {HOME}/autostart_pikaraoke.py"
        new = []
        replaced = False
        for line in content.splitlines():
            if line.startswith("Exec="):
                new.append(exec_line)
                replaced = True
            else:
                new.append(line)
        if not replaced:
            new.append(exec_line)
        DESKTOP_FILE_PATH.write_text("\n".join(new) + "\n")
    else:
        DESKTOP_FILE_PATH.write_text(
            f"""[Desktop Entry]
Name=Start PiKaraoke
Comment=Launch PiKaraoke on boot
Exec={VENV_DIR}/bin/python {HOME}/autostart_pikaraoke.py
Icon=utilities-terminal
Terminal=false
Type=Application
X-GNOME-Autostart-enabled=true
"""
        )
    # pk_aliases
    aliases_src = ASSETS_DIR / "pk_aliases"
    if aliases_src.exists():
        shutil.copy2(aliases_src, HOME / ".pk_aliases")
        ensure_rc_sourced(HOME / ".bashrc")
        ensure_rc_sourced(HOME / ".zshrc")


def ensure_rc_sourced(rc_path: Path):
    try:
        rc_path.touch(exist_ok=True)
        text = rc_path.read_text()
        marker = "# >>> deskpi-karaoke aliases >>>"
        block = f"""\n{marker}\n[ -f "$HOME/.pk_aliases" ] && source "$HOME/.pk_aliases"\n# <<< deskpi-karaoke aliases <<<\n"""
        if marker not in text:
            rc_path.write_text(text.rstrip() + block)
    except Exception as e:
        print(f"⚠️  Could not update {rc_path}: {e}")


def git(cmd: str, default: Optional[str] = None) -> Optional[str]:
    try:
        out = run(
            ["git"] + cmd.split(), check=True, cwd=str(REPO_ROOT), capture_output=True
        ).stdout.strip()
        return out
    except Exception:
        return default


def record_state():
    print_h("Recording installer state")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    branch = git("rev-parse --abbrev-ref HEAD", default="unknown") or "unknown"
    if branch in ("dev", "develop"):
        sha = git("rev-parse HEAD", default="") or ""
        if sha:
            (STATE_DIR / ".last_applied_sha_dev").write_text(sha + "\n")
            print(f"dev branch detected; recorded SHA {sha}")
    else:
        tag = git("describe --tags --abbrev=0", default="") or ""
        if tag:
            (STATE_DIR / "VERSION").write_text(tag + "\n")
            print(f"main/tagged install; recorded VERSION {tag}")
        else:
            # fallback — still write something so pk update logic has a file
            (STATE_DIR / "VERSION").write_text("0.0.0\n")
            print("No tag found; wrote VERSION 0.0.0")


def main():
    print_h("PiKaraoke Installer (dev)")
    ensure_python_version()
    check_platform()
    apt_install()
    py = ensure_venv()
    copy_assets()
    record_state()

    print_h("All done")
    print("• Venv       :", VENV_DIR)
    print("• Autostart  :", DESKTOP_FILE_PATH)
    print("• State dir  :", STATE_DIR)
    print(
        "\nYou may need to log out and back in (or reboot) for autostart changes to take effect."
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        sys.exit(130)
    except SystemExit as e:
        raise
    except Exception as e:
        print(f"❌ Installer failed: {e}")
        sys.exit(1)
