"""Low-level shell/process helpers shared by install and uninstall scripts."""

import shutil
import subprocess
from pathlib import Path


def print_h(msg: str):
    print(f"\n=== {msg} ===")


def run(cmd, check=True, cwd=None, env=None, capture_output=False, text=True):
    if isinstance(cmd, str):
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


def safe_remove(path: Path):
    """Removes a file or directory if it exists — skips if 'pikaraoke-songs' is in path"""
    if not path.exists():
        return

    if path.is_dir() and "pikaraoke-songs" in path.name.lower():
        print(f"🚫 Skipping songs folder: {path}")
        return

    try:
        if path.is_dir():
            shutil.rmtree(path)
            print(f"🗑️ Removed directory: {path}")
        else:
            path.unlink()
            print(f"🗑️ Removed file: {path}")
    except Exception as e:
        print(f"❌ Error removing {path}: {e}")


def stop_service(name):
    """Stops and disables a systemd service"""
    subprocess.run(["sudo", "systemctl", "stop", name], check=False)
    subprocess.run(["sudo", "systemctl", "disable", name], check=False)
