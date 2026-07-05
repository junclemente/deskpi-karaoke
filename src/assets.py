"""Copies autostart/UI assets and desktop entry into $HOME, and patches shell rc files."""

import shutil
from pathlib import Path

from src.constants import ASSETS_DIR, AUTOSTART_DIR, DESKTOP_FILE_PATH, HOME, VENV_DIR
from src.shell import print_h


def copy_assets():
    print_h("Copying assets to $HOME")
    AUTOSTART_DIR.mkdir(parents=True, exist_ok=True)
    # autostart script & UI
    shutil.copy2(ASSETS_DIR / "autostart_pikaraoke.py", HOME / "autostart_pikaraoke.py")
    shutil.copy2(ASSETS_DIR / "pikaraoke_ui.py", HOME / "pikaraoke_ui.py")
    # desktop entry
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
