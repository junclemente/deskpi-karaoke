from unittest.mock import Mock

import uninstall_clean


def _fake_args(deskpi=False):
    import argparse

    return argparse.Namespace(deskpi=deskpi)


def test_remove_virtualenvs_removes_both_legacy_and_current(tmp_path, monkeypatch):
    venv_dir = tmp_path / ".venv-pikaraoke"
    legacy_venv = tmp_path / ".venv"
    venv_dir.mkdir()
    legacy_venv.mkdir()
    monkeypatch.setattr(uninstall_clean.constants, "HOME", tmp_path)
    monkeypatch.setattr(uninstall_clean.constants, "VENV_DIR", venv_dir)

    uninstall_clean.remove_virtualenvs()

    assert not venv_dir.exists()
    assert not legacy_venv.exists()


def test_remove_copied_assets_removes_all_current_files(tmp_path, monkeypatch):
    autostart_script = tmp_path / "autostart_pikaraoke.py"
    ui_path = tmp_path / "pikaraoke_ui.py"
    state_toml_helper = tmp_path / "state_toml.py"
    icon_path = tmp_path / "pikaraoke_icon.png"
    for p in (autostart_script, ui_path, state_toml_helper, icon_path):
        p.write_text("x")

    monkeypatch.setattr(
        uninstall_clean.constants, "AUTOSTART_SCRIPT_PATH", autostart_script
    )
    monkeypatch.setattr(uninstall_clean.constants, "PIKARAOKE_UI_PATH", ui_path)
    monkeypatch.setattr(
        uninstall_clean.constants, "STATE_TOML_HELPER_PATH", state_toml_helper
    )
    monkeypatch.setattr(uninstall_clean.constants, "ICON_PATH", icon_path)

    uninstall_clean.remove_copied_assets()

    assert not autostart_script.exists()
    assert not ui_path.exists()
    assert not state_toml_helper.exists()
    assert not icon_path.exists()


def test_remove_shortcuts_and_scripts_removes_current_and_legacy(tmp_path, monkeypatch):
    shortcut = tmp_path / "Desktop" / "Start PiKaraoke.desktop"
    shortcut.parent.mkdir()
    shortcut.write_text("x")
    legacy_icons = [
        shortcut.parent / "start_pikaraoke.desktop",
        shortcut.parent / "UpgradePikaraoke.desktop",
    ]
    for p in legacy_icons:
        p.write_text("x")
    legacy_sh = tmp_path / "pikaraoke_start_script.sh"
    legacy_launcher = tmp_path / "pikaraoke_launcher.sh"
    legacy_start_py = tmp_path / "pikaraoke_start.py"
    for p in (legacy_sh, legacy_launcher, legacy_start_py):
        p.write_text("x")

    monkeypatch.setattr(uninstall_clean.constants, "HOME", tmp_path)
    monkeypatch.setattr(uninstall_clean.constants, "DESKTOP_SHORTCUT_PATH", shortcut)
    monkeypatch.setattr(uninstall_clean.constants, "DESKTOP_DIR", shortcut.parent)

    uninstall_clean.remove_shortcuts_and_scripts()

    assert not shortcut.exists()
    assert not any(p.exists() for p in legacy_icons)
    assert not legacy_sh.exists()
    assert not legacy_launcher.exists()
    assert not legacy_start_py.exists()


def test_remove_autostart_config_removes_current_path(tmp_path, monkeypatch):
    """Regression test: uninstall_clean previously only swept the legacy
    system-wide autostart path and never removed the one copy_assets()
    actually writes, so PiKaraoke kept auto-launching after "uninstalling"."""
    autostart_entry = tmp_path / ".config" / "autostart" / "pikaraoke.desktop"
    autostart_entry.parent.mkdir(parents=True)
    autostart_entry.write_text("[Desktop Entry]\n")
    legacy_entry = tmp_path / "legacy" / "pikaraoke.desktop"
    monkeypatch.setattr(uninstall_clean.constants, "DESKTOP_FILE_PATH", autostart_entry)
    monkeypatch.setattr(
        uninstall_clean.constants, "LEGACY_XDG_AUTOSTART_PATH", legacy_entry
    )

    uninstall_clean.remove_autostart_config()

    assert not autostart_entry.exists()


def test_remove_autostart_config_also_sweeps_legacy_xdg_path(tmp_path, monkeypatch):
    legacy_entry = tmp_path / "legacy" / "pikaraoke.desktop"
    legacy_entry.parent.mkdir(parents=True)
    legacy_entry.write_text("[Desktop Entry]\n")
    monkeypatch.setattr(
        uninstall_clean.constants, "DESKTOP_FILE_PATH", tmp_path / "nonexistent"
    )
    monkeypatch.setattr(
        uninstall_clean.constants, "LEGACY_XDG_AUTOSTART_PATH", legacy_entry
    )

    uninstall_clean.remove_autostart_config()

    assert not legacy_entry.exists()


def test_remove_pk_aliases_removes_file_and_rc_blocks(tmp_path, monkeypatch):
    home = tmp_path
    pk_aliases = home / ".pk_aliases"
    pk_aliases.write_text("# aliases")
    bashrc = home / ".bashrc"
    from src.assets import ensure_rc_sourced

    bashrc.write_text("existing content\n")
    ensure_rc_sourced(bashrc)

    monkeypatch.setattr(uninstall_clean.constants, "PK_ALIASES_PATH", pk_aliases)
    monkeypatch.setattr(uninstall_clean.constants, "HOME", home)

    uninstall_clean.remove_pk_aliases()

    assert not pk_aliases.exists()
    assert "existing content" in bashrc.read_text()
    assert "deskpi-karaoke" not in bashrc.read_text()


def test_remove_state_dir_removes_state_directory(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    state_dir.mkdir()
    monkeypatch.setattr(uninstall_clean.constants, "STATE_DIR", state_dir)

    uninstall_clean.remove_state_dir()

    assert not state_dir.exists()


def test_remove_ytdlp_config_removes_config_dir(tmp_path, monkeypatch):
    cfg_dir = tmp_path / ".config" / "yt-dlp"
    cfg_dir.mkdir(parents=True)
    monkeypatch.setattr(uninstall_clean.constants, "YTDLP_CONFIG_DIR", cfg_dir)

    uninstall_clean.remove_ytdlp_config()

    assert not cfg_dir.exists()


def test_remove_legacy_install_folder_skips_when_songs_present(tmp_path, monkeypatch):
    pikaraoke_dir = tmp_path / "pikaraoke"
    pikaraoke_dir.mkdir()
    (pikaraoke_dir / "pikaraoke-songs").mkdir()
    monkeypatch.setattr(uninstall_clean.constants, "HOME", tmp_path)

    uninstall_clean.remove_legacy_install_folder()

    assert pikaraoke_dir.exists()


def test_remove_legacy_install_folder_removes_when_no_songs(tmp_path, monkeypatch):
    pikaraoke_dir = tmp_path / "pikaraoke"
    pikaraoke_dir.mkdir()
    (pikaraoke_dir / "some_file.txt").write_text("x")
    monkeypatch.setattr(uninstall_clean.constants, "HOME", tmp_path)

    uninstall_clean.remove_legacy_install_folder()

    assert not pikaraoke_dir.exists()


def test_main_calls_all_removal_steps_in_order(monkeypatch):
    calls = []

    def tracker(name):
        return lambda *a, **k: calls.append(name)

    monkeypatch.setattr(uninstall_clean, "parse_args", lambda: _fake_args(deskpi=False))
    monkeypatch.setattr(uninstall_clean, "setup_logging", Mock())
    for name in (
        "remove_virtualenvs",
        "remove_copied_assets",
        "remove_shortcuts_and_scripts",
        "remove_logs",
        "remove_autostart_config",
        "remove_logrotate_config",
        "remove_pk_aliases",
        "remove_state_dir",
        "remove_ytdlp_config",
        "remove_legacy_install_folder",
    ):
        monkeypatch.setattr(uninstall_clean, name, tracker(name))
    fake_deskpi = Mock()
    monkeypatch.setattr(uninstall_clean, "remove_deskpi_drivers", fake_deskpi)

    uninstall_clean.main()

    assert calls == [
        "remove_virtualenvs",
        "remove_copied_assets",
        "remove_shortcuts_and_scripts",
        "remove_logs",
        "remove_autostart_config",
        "remove_logrotate_config",
        "remove_pk_aliases",
        "remove_state_dir",
        "remove_ytdlp_config",
        "remove_legacy_install_folder",
    ]
    fake_deskpi.assert_not_called()


def test_main_removes_deskpi_drivers_when_flag_set(monkeypatch):
    monkeypatch.setattr(uninstall_clean, "parse_args", lambda: _fake_args(deskpi=True))
    monkeypatch.setattr(uninstall_clean, "setup_logging", Mock())
    for name in (
        "remove_virtualenvs",
        "remove_copied_assets",
        "remove_shortcuts_and_scripts",
        "remove_logs",
        "remove_autostart_config",
        "remove_logrotate_config",
        "remove_pk_aliases",
        "remove_state_dir",
        "remove_ytdlp_config",
        "remove_legacy_install_folder",
    ):
        monkeypatch.setattr(uninstall_clean, name, Mock())
    fake_deskpi = Mock()
    monkeypatch.setattr(uninstall_clean, "remove_deskpi_drivers", fake_deskpi)

    uninstall_clean.main()

    fake_deskpi.assert_called_once()
