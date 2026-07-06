"""Low-level shell/process helpers shared by install and uninstall scripts."""

import logging
import shutil
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


def log_section(msg: str):
    logger.info("\n=== %s ===", msg)


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
    """Removes a file/dir if it exists — skips paths containing 'pikaraoke-songs'."""
    if not path.exists():
        return

    if path.is_dir() and "pikaraoke-songs" in path.name.lower():
        logger.warning("🚫 Skipping songs folder: %s", path)
        return

    try:
        if path.is_dir():
            shutil.rmtree(path)
            logger.info("🗑️ Removed directory: %s", path)
        else:
            path.unlink()
            logger.info("🗑️ Removed file: %s", path)
    except Exception as e:
        logger.error("❌ Error removing %s: %s", path, e)


def stop_service(name):
    """Stops and disables a systemd service"""
    subprocess.run(["sudo", "systemctl", "stop", name], check=False)
    subprocess.run(["sudo", "systemctl", "disable", name], check=False)
