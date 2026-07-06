"""Copies autostart/UI assets and desktop entry into $HOME, patches shell rc files."""

import logging
import shutil
from pathlib import Path

from src import constants
from src.shell import log_section

logger = logging.getLogger(__name__)


def copy_assets():
    log_section("Copying assets to $HOME")
    constants.AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    # autostart script, UI, and the shared state-file helper it imports
    shutil.copy2(
        constants.ASSETS_DIR / "autostart_pikaraoke.py",
        constants.HOME / "autostart_pikaraoke.py",
    )
    shutil.copy2(
        constants.ASSETS_DIR / "pikaraoke_ui.py", constants.HOME / "pikaraoke_ui.py"
    )
    shutil.copy2(
        constants.ASSETS_DIR / "state_toml.py", constants.HOME / "state_toml.py"
    )
    # desktop entry
    constants.DESKTOP_FILE_PATH.write_text(
        f"""[Desktop Entry]
Name=Start PiKaraoke
Comment=Launch PiKaraoke on boot
Exec={constants.VENV_DIR}/bin/python {constants.HOME}/autostart_pikaraoke.py
Icon=utilities-terminal
Terminal=false
Type=Application
X-GNOME-Autostart-enabled=true
"""
    )
    # desktop icon the user can click to launch PiKaraoke on demand
    constants.DESKTOP_DIR.mkdir(parents=True, exist_ok=True)
    constants.DESKTOP_SHORTCUT_PATH.write_text(
        f"""[Desktop Entry]
Name=Start PiKaraoke
Comment=Launch PiKaraoke
Exec={constants.VENV_DIR}/bin/python {constants.HOME}/autostart_pikaraoke.py
Icon=utilities-terminal
Terminal=false
Type=Application
"""
    )
    # LXDE/PCManFM refuses to run a double-clicked .desktop file that isn't
    # marked executable, showing a "trust" prompt instead of launching it.
    constants.DESKTOP_SHORTCUT_PATH.chmod(0o755)
    # pk_aliases
    aliases_src = constants.ASSETS_DIR / "pk_aliases"
    if aliases_src.exists():
        shutil.copy2(aliases_src, constants.HOME / ".pk_aliases")
        ensure_rc_sourced(constants.HOME / ".bashrc")
        ensure_rc_sourced(constants.HOME / ".zshrc")


def ensure_rc_sourced(rc_path: Path):
    try:
        rc_path.touch(exist_ok=True)
        text = rc_path.read_text()
        marker = "# >>> deskpi-karaoke aliases >>>"
        source_line = '[ -f "$HOME/.pk_aliases" ] && source "$HOME/.pk_aliases"'
        block = f"\n{marker}\n{source_line}\n# <<< deskpi-karaoke aliases <<<\n"
        if marker not in text:
            rc_path.write_text(text.rstrip() + block)
    except Exception as e:
        logger.warning("⚠️  Could not update %s: %s", rc_path, e)
