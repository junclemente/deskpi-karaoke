from unittest.mock import Mock

import uninstall


def _fake_args(deskpi=False):
    import argparse

    return argparse.Namespace(deskpi=deskpi)


def test_remove_current_virtualenv_removes_venv_dir(tmp_path, monkeypatch):
    venv_dir = tmp_path / ".venv-pikaraoke"
    venv_dir.mkdir()
    monkeypatch.setattr(uninstall.constants, "VENV_DIR", venv_dir)

    uninstall.remove_current_virtualenv()

    assert not venv_dir.exists()


def test_remove_copied_assets_removes_all_current_files(tmp_path, monkeypatch):
    autostart_script = tmp_path / "autostart_pikaraoke.py"
    ui_path = tmp_path / "pikaraoke_ui.py"
    state_toml_helper = tmp_path / "state_toml.py"
    icon_path = tmp_path / "pikaraoke_icon.png"
    for p in (autostart_script, ui_path, state_toml_helper, icon_path):
        p.write_text("x")

    monkeypatch.setattr(uninstall.constants, "AUTOSTART_SCRIPT_PATH", autostart_script)
    monkeypatch.setattr(uninstall.constants, "PIKARAOKE_UI_PATH", ui_path)
    monkeypatch.setattr(
        uninstall.constants, "STATE_TOML_HELPER_PATH", state_toml_helper
    )
    monkeypatch.setattr(uninstall.constants, "ICON_PATH", icon_path)

    uninstall.remove_copied_assets()

    assert not autostart_script.exists()
    assert not ui_path.exists()
    assert not state_toml_helper.exists()
    assert not icon_path.exists()


def test_remove_shortcut_removes_desktop_shortcut(tmp_path, monkeypatch):
    shortcut = tmp_path / "Desktop" / "Start PiKaraoke.desktop"
    shortcut.parent.mkdir()
    shortcut.write_text("x")
    monkeypatch.setattr(uninstall.constants, "DESKTOP_SHORTCUT_PATH", shortcut)

    uninstall.remove_shortcut()

    assert not shortcut.exists()


def test_remove_autostart_removes_the_current_autostart_entry(tmp_path, monkeypatch):
    """Regression test: uninstall used to remove the wrong (legacy system-wide)
    autostart path and never touched the one copy_assets() actually writes,
    so PiKaraoke kept auto-launching on the next boot after "uninstalling"."""
    autostart_entry = tmp_path / ".config" / "autostart" / "pikaraoke.desktop"
    autostart_entry.parent.mkdir(parents=True)
    autostart_entry.write_text("[Desktop Entry]\n")
    monkeypatch.setattr(uninstall.constants, "DESKTOP_FILE_PATH", autostart_entry)

    uninstall.remove_autostart()

    assert not autostart_entry.exists()


def test_remove_pk_aliases_removes_file_and_rc_blocks(tmp_path, monkeypatch):
    home = tmp_path
    pk_aliases = home / ".pk_aliases"
    pk_aliases.write_text("# aliases")
    bashrc = home / ".bashrc"
    zshrc = home / ".zshrc"
    from src.assets import ensure_rc_sourced

    bashrc.write_text("existing bashrc content\n")
    zshrc.write_text("existing zshrc content\n")
    ensure_rc_sourced(bashrc)
    ensure_rc_sourced(zshrc)

    monkeypatch.setattr(uninstall.constants, "PK_ALIASES_PATH", pk_aliases)
    monkeypatch.setattr(uninstall.constants, "HOME", home)

    uninstall.remove_pk_aliases()

    assert not pk_aliases.exists()
    assert "existing bashrc content" in bashrc.read_text()
    assert "deskpi-karaoke" not in bashrc.read_text()
    assert "existing zshrc content" in zshrc.read_text()
    assert "deskpi-karaoke" not in zshrc.read_text()


def test_remove_state_dir_removes_state_directory(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    state_dir.mkdir()
    (state_dir / "state.toml").write_text("[state]\n")
    monkeypatch.setattr(uninstall.constants, "STATE_DIR", state_dir)

    uninstall.remove_state_dir()

    assert not state_dir.exists()


def test_remove_ytdlp_config_removes_config_dir(tmp_path, monkeypatch):
    cfg_dir = tmp_path / ".config" / "yt-dlp"
    cfg_dir.mkdir(parents=True)
    (cfg_dir / "config").write_text("--js-runtimes deno\n")
    monkeypatch.setattr(uninstall.constants, "YTDLP_CONFIG_DIR", cfg_dir)

    uninstall.remove_ytdlp_config()

    assert not cfg_dir.exists()


def test_main_calls_all_removal_steps_without_deskpi(monkeypatch):
    calls = []

    def tracker(name):
        return lambda *a, **k: calls.append(name)

    monkeypatch.setattr(uninstall, "parse_args", lambda: _fake_args(deskpi=False))
    monkeypatch.setattr(uninstall, "setup_logging", Mock())
    for name in (
        "remove_current_virtualenv",
        "remove_start_script",
        "remove_copied_assets",
        "remove_shortcut",
        "remove_logs",
        "remove_autostart",
        "remove_logrotate_config",
        "remove_pk_aliases",
        "remove_state_dir",
        "remove_ytdlp_config",
    ):
        monkeypatch.setattr(uninstall, name, tracker(name))
    fake_deskpi = Mock()
    monkeypatch.setattr(uninstall, "remove_deskpi_drivers", fake_deskpi)

    uninstall.main()

    assert calls == [
        "remove_current_virtualenv",
        "remove_start_script",
        "remove_copied_assets",
        "remove_shortcut",
        "remove_logs",
        "remove_autostart",
        "remove_logrotate_config",
        "remove_pk_aliases",
        "remove_state_dir",
        "remove_ytdlp_config",
    ]
    fake_deskpi.assert_not_called()


def test_main_removes_deskpi_drivers_when_flag_set(monkeypatch):
    monkeypatch.setattr(uninstall, "parse_args", lambda: _fake_args(deskpi=True))
    monkeypatch.setattr(uninstall, "setup_logging", Mock())
    for name in (
        "remove_current_virtualenv",
        "remove_start_script",
        "remove_copied_assets",
        "remove_shortcut",
        "remove_logs",
        "remove_autostart",
        "remove_logrotate_config",
        "remove_pk_aliases",
        "remove_state_dir",
        "remove_ytdlp_config",
    ):
        monkeypatch.setattr(uninstall, name, Mock())
    fake_deskpi = Mock()
    monkeypatch.setattr(uninstall, "remove_deskpi_drivers", fake_deskpi)

    uninstall.main()

    fake_deskpi.assert_called_once()
