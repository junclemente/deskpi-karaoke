import importlib
import os
import subprocess
import sys
from pathlib import Path

import pytest

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
SHIM = ASSETS_DIR / "chromium-browser"


@pytest.fixture
def autostart(tmp_path, monkeypatch):
    # The launcher opens its log file and rewrites PATH at import time, so
    # point HOME at tmp_path and restore PATH afterwards.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("PATH", os.environ["PATH"])
    monkeypatch.syspath_prepend(str(ASSETS_DIR))
    sys.modules.pop("autostart_pikaraoke", None)
    return importlib.import_module("autostart_pikaraoke")


def test_shim_dir_is_first_on_path(autostart, tmp_path):
    first = os.environ["PATH"].split(":")[0]
    assert first == str(tmp_path / ".deskpi-karaoke" / "bin")


def test_shim_is_valid_sh_and_forces_x11():
    subprocess.run(["sh", "-n", str(SHIM)], check=True)
    assert "--ozone-platform=x11" in SHIM.read_text()
    assert SHIM.stat().st_mode & 0o111 == 0o111
