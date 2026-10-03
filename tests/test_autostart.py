import importlib
import sys
from pathlib import Path

import pytest

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


@pytest.fixture
def autostart(tmp_path, monkeypatch):
    # The launcher opens its log file under $HOME at import time, so point
    # HOME at tmp_path to keep the test from writing into the real home.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.syspath_prepend(str(ASSETS_DIR))
    sys.modules.pop("autostart_pikaraoke", None)
    return importlib.import_module("autostart_pikaraoke")


def test_browser_env_forces_x11(autostart):
    base = {"WAYLAND_DISPLAY": "wayland-1", "PATH": "/bin"}

    env = autostart.browser_env(base)

    assert "WAYLAND_DISPLAY" not in env
    assert env["DISPLAY"] == ":0"
    assert env["CHROMIUM_FLAGS"] == "--ozone-platform=x11"
    assert env["PATH"] == "/bin"
    assert base["WAYLAND_DISPLAY"] == "wayland-1"  # caller's env untouched


def test_browser_env_keeps_existing_display_and_flags(autostart):
    env = autostart.browser_env(
        {"DISPLAY": ":1", "CHROMIUM_FLAGS": "--foo --ozone-platform=wayland"}
    )

    assert env["DISPLAY"] == ":1"
    assert env["CHROMIUM_FLAGS"] == "--foo --ozone-platform=wayland"
