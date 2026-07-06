"""Copies autostart/UI assets and desktop entry into $HOME, patches shell rc files."""

import configparser
import logging
import re
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
        constants.AUTOSTART_SCRIPT_PATH,
    )
    shutil.copy2(constants.ASSETS_DIR / "pikaraoke_ui.py", constants.PIKARAOKE_UI_PATH)
    shutil.copy2(
        constants.ASSETS_DIR / "state_toml.py", constants.STATE_TOML_HELPER_PATH
    )
    shutil.copy2(constants.ASSETS_DIR / "pikaraoke_icon.png", constants.ICON_PATH)
    # desktop entry
    constants.DESKTOP_FILE_PATH.write_text(
        f"""[Desktop Entry]
Name=Start PiKaraoke
Comment=Launch PiKaraoke on boot
Exec={constants.VENV_DIR}/bin/python {constants.AUTOSTART_SCRIPT_PATH}
Icon={constants.ICON_PATH}
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
Exec={constants.VENV_DIR}/bin/python {constants.AUTOSTART_SCRIPT_PATH}
Icon={constants.ICON_PATH}
Terminal=false
Type=Application
"""
    )
    # LXDE/PCManFM refuses to run a double-clicked .desktop file that isn't
    # marked executable, showing a "trust" prompt instead of launching it.
    constants.DESKTOP_SHORTCUT_PATH.chmod(0o755)
    enable_quick_exec()
    # pk_aliases
    aliases_src = constants.ASSETS_DIR / "pk_aliases"
    if aliases_src.exists():
        shutil.copy2(aliases_src, constants.PK_ALIASES_PATH)
        ensure_rc_sourced(constants.HOME / ".bashrc")
        ensure_rc_sourced(constants.HOME / ".zshrc")


def enable_quick_exec():
    """Set libfm's quick_exec so PCManFM launches an executable .desktop file
    directly instead of prompting "Execute/Execute in Terminal/Open/Cancel"
    on every double-click — same effect as its Edit > Preferences > "Don't
    ask options on launch executable file" checkbox."""
    path = constants.LIBFM_CONFIG_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        config = configparser.RawConfigParser()
        if path.exists():
            config.read(path)
        if not config.has_section("config"):
            config.add_section("config")
        config.set("config", "quick_exec", "1")
        with path.open("w") as f:
            config.write(f, space_around_delimiters=False)
    except Exception as e:
        logger.warning("⚠️  Could not enable quick_exec in %s: %s", path, e)


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


_RC_BLOCK_PATTERN = re.compile(
    r"\n?# >>> deskpi-karaoke aliases >>>.*?# <<< deskpi-karaoke aliases <<<\n?",
    re.DOTALL,
)


def remove_rc_block(rc_path: Path):
    """Reverse of ensure_rc_sourced: strip the marked block it added, if any."""
    try:
        if not rc_path.exists():
            return
        text = rc_path.read_text()
        new_text = _RC_BLOCK_PATTERN.sub("", text)
        if new_text != text:
            rc_path.write_text(new_text)
    except Exception as e:
        logger.warning("⚠️  Could not clean up %s: %s", rc_path, e)
