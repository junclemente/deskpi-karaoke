"""Shared paths and configuration constants for the installer."""

from pathlib import Path

HOME = Path.home()
VENV_DIR = HOME / ".venv-pikaraoke"
STATE_DIR = HOME / ".deskpi-karaoke"
REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
AUTOSTART_DIR = HOME / ".config" / "autostart"
DESKTOP_FILE_PATH = AUTOSTART_DIR / "pikaraoke.desktop"

PY_MIN = (3, 10)

PKG_CORE = [
    "pip>=24.0",
    "setuptools>=68",
    "wheel",
    "packaging>=24.0",
    "yt-dlp",
    "pikaraoke==1.18.0",  # pinned: 1.19.0 has breaking splash screen bug
]

APT_PKGS = [
    "python3-venv",
    "python3-pip",
    "ffmpeg",
    "nodejs",
    "npm",
    "curl",
]
