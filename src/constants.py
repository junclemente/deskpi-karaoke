"""Shared paths and configuration constants for the installer.

Install-time tunables (Python floor, package lists) live in config.toml at
the repo root so they're editable without touching Python source; loaded
here via the stdlib tomllib reader (Python 3.11+).
"""

import tomllib
from pathlib import Path

HOME = Path.home()
VENV_DIR = HOME / ".venv-pikaraoke"
STATE_DIR = HOME / ".deskpi-karaoke"
# X11 Chromium shim dir; autostart_pikaraoke.py hardcodes the same path
# since it runs from $HOME without access to this package.
SHIM_BIN_DIR = STATE_DIR / "bin"
CHROMIUM_SHIM_PATH = SHIM_BIN_DIR / "chromium-browser"
REPO_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = REPO_ROOT / "assets"
AUTOSTART_DIR = HOME / ".config" / "autostart"
DESKTOP_FILE_PATH = AUTOSTART_DIR / "pikaraoke.desktop"
DESKTOP_DIR = HOME / "Desktop"
DESKTOP_SHORTCUT_PATH = DESKTOP_DIR / "Start PiKaraoke.desktop"
# Desktop icons from the pre-installer manual setup (Oct 2024) that launched
# pikaraoke from the old ~/.venv via lxterminal. Nothing current creates
# them, but install.py and uninstall_clean.py sweep them so upgraded Pis
# don't keep a stale second "Start" icon pointing at a dead venv.
LEGACY_DESKTOP_SHORTCUT_NAMES = ("start_pikaraoke.desktop", "UpgradePikaraoke.desktop")
LIBFM_CONFIG_PATH = HOME / ".config" / "libfm" / "libfm.conf"
ICON_PATH = HOME / "pikaraoke_icon.png"
AUTOSTART_SCRIPT_PATH = HOME / "autostart_pikaraoke.py"
PIKARAOKE_UI_PATH = HOME / "pikaraoke_ui.py"
STATE_TOML_HELPER_PATH = HOME / "state_toml.py"
PK_ALIASES_PATH = HOME / ".pk_aliases"
YTDLP_CONFIG_DIR = HOME / ".config" / "yt-dlp"
# System-wide autostart path from a much older install scheme (pre
# system/user split) — nothing current creates it, but uninstall_clean.py
# sweeps it as a legacy leftover.
LEGACY_XDG_AUTOSTART_PATH = Path("/etc/xdg/autostart/pikaraoke.desktop")

CONFIG_FILE = REPO_ROOT / "config.toml"

with CONFIG_FILE.open("rb") as _f:
    _config = tomllib.load(_f)

PY_MIN = tuple(
    int(part) for part in _config["install"]["python_min_version"].split(".")
)
PKG_CORE = _config["install"]["packages"]["core"]
APT_PKGS = _config["install"]["packages"]["apt"]
