from src import assets


def test_ensure_rc_sourced_appends_block_when_missing(tmp_path):
    rc = tmp_path / ".bashrc"
    rc.write_text("existing content\n")

    assets.ensure_rc_sourced(rc)

    text = rc.read_text()
    assert "existing content" in text
    assert "# >>> deskpi-karaoke aliases >>>" in text
    assert '[ -f "$HOME/.pk_aliases" ] && source "$HOME/.pk_aliases"' in text


def test_ensure_rc_sourced_creates_file_if_absent(tmp_path):
    rc = tmp_path / ".zshrc"

    assets.ensure_rc_sourced(rc)

    assert rc.exists()
    assert "# >>> deskpi-karaoke aliases >>>" in rc.read_text()


def test_ensure_rc_sourced_is_idempotent(tmp_path):
    rc = tmp_path / ".bashrc"
    rc.write_text("existing content\n")

    assets.ensure_rc_sourced(rc)
    assets.ensure_rc_sourced(rc)

    assert rc.read_text().count("# >>> deskpi-karaoke aliases >>>") == 1


def test_remove_rc_block_strips_block_added_by_ensure_rc_sourced(tmp_path):
    rc = tmp_path / ".bashrc"
    rc.write_text("existing content\n")
    assets.ensure_rc_sourced(rc)
    assert "# >>> deskpi-karaoke aliases >>>" in rc.read_text()

    assets.remove_rc_block(rc)

    text = rc.read_text()
    assert "existing content" in text
    assert "# >>> deskpi-karaoke aliases >>>" not in text
    assert "deskpi-karaoke" not in text


def test_remove_rc_block_preserves_content_after_the_block(tmp_path):
    rc = tmp_path / ".bashrc"
    assets.ensure_rc_sourced(rc)
    rc.write_text(rc.read_text() + "\nsome later line\n")

    assets.remove_rc_block(rc)

    text = rc.read_text()
    assert "some later line" in text
    assert "deskpi-karaoke" not in text


def test_remove_rc_block_noop_when_marker_absent(tmp_path):
    rc = tmp_path / ".bashrc"
    rc.write_text("unrelated content\n")

    assets.remove_rc_block(rc)

    assert rc.read_text() == "unrelated content\n"


def test_remove_rc_block_noop_when_file_missing(tmp_path):
    rc = tmp_path / ".bashrc"

    assets.remove_rc_block(rc)  # should not raise

    assert not rc.exists()


def test_enable_quick_exec_creates_config_when_absent(tmp_path, monkeypatch):
    libfm_conf = tmp_path / ".config" / "libfm" / "libfm.conf"
    monkeypatch.setattr(assets.constants, "LIBFM_CONFIG_PATH", libfm_conf)

    assets.enable_quick_exec()

    text = libfm_conf.read_text()
    assert "[config]" in text
    assert "quick_exec=1" in text


def test_enable_quick_exec_preserves_existing_settings(tmp_path, monkeypatch):
    libfm_conf = tmp_path / ".config" / "libfm" / "libfm.conf"
    libfm_conf.parent.mkdir(parents=True)
    libfm_conf.write_text(
        "[config]\n"
        "terminal=lxterminal -e %s\n"
        "single_click=0\n"
        "\n"
        "[ui]\n"
        "big_icon_size=48\n"
    )
    monkeypatch.setattr(assets.constants, "LIBFM_CONFIG_PATH", libfm_conf)

    assets.enable_quick_exec()

    text = libfm_conf.read_text()
    assert "terminal=lxterminal -e %s" in text
    assert "single_click=0" in text
    assert "big_icon_size=48" in text
    assert "quick_exec=1" in text


def test_enable_quick_exec_is_idempotent(tmp_path, monkeypatch):
    libfm_conf = tmp_path / ".config" / "libfm" / "libfm.conf"
    monkeypatch.setattr(assets.constants, "LIBFM_CONFIG_PATH", libfm_conf)

    assets.enable_quick_exec()
    assets.enable_quick_exec()

    assert libfm_conf.read_text().count("quick_exec") == 1


def test_copy_assets_copies_files_and_writes_desktop_entry(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "autostart_pikaraoke.py").write_text("# autostart stub")
    (assets_dir / "pikaraoke_ui.py").write_text("# ui stub")
    (assets_dir / "state_toml.py").write_text("# state_toml stub")
    (assets_dir / "pikaraoke_icon.png").write_text("# icon stub")
    (assets_dir / "pk_aliases").write_text("# aliases stub")

    venv_dir = home / ".venv-pikaraoke"
    autostart_dir = home / ".config" / "autostart"
    desktop_file = autostart_dir / "pikaraoke.desktop"
    desktop_dir = home / "Desktop"
    desktop_shortcut = desktop_dir / "Start PiKaraoke.desktop"
    icon_path = home / "pikaraoke_icon.png"
    autostart_script_path = home / "autostart_pikaraoke.py"
    pikaraoke_ui_path = home / "pikaraoke_ui.py"
    state_toml_helper_path = home / "state_toml.py"
    pk_aliases_path = home / ".pk_aliases"

    monkeypatch.setattr(assets.constants, "HOME", home)
    monkeypatch.setattr(assets.constants, "ASSETS_DIR", assets_dir)
    monkeypatch.setattr(assets.constants, "VENV_DIR", venv_dir)
    monkeypatch.setattr(assets.constants, "AUTOSTART_DIR", autostart_dir)
    monkeypatch.setattr(assets.constants, "DESKTOP_FILE_PATH", desktop_file)
    monkeypatch.setattr(assets.constants, "DESKTOP_DIR", desktop_dir)
    monkeypatch.setattr(assets.constants, "DESKTOP_SHORTCUT_PATH", desktop_shortcut)
    monkeypatch.setattr(assets.constants, "ICON_PATH", icon_path)
    monkeypatch.setattr(
        assets.constants, "AUTOSTART_SCRIPT_PATH", autostart_script_path
    )
    monkeypatch.setattr(assets.constants, "PIKARAOKE_UI_PATH", pikaraoke_ui_path)
    monkeypatch.setattr(
        assets.constants, "STATE_TOML_HELPER_PATH", state_toml_helper_path
    )
    monkeypatch.setattr(assets.constants, "PK_ALIASES_PATH", pk_aliases_path)
    libfm_conf = home / ".config" / "libfm" / "libfm.conf"
    monkeypatch.setattr(assets.constants, "LIBFM_CONFIG_PATH", libfm_conf)

    assets.copy_assets()

    assert autostart_script_path.read_text() == "# autostart stub"
    assert pikaraoke_ui_path.read_text() == "# ui stub"
    assert state_toml_helper_path.read_text() == "# state_toml stub"
    assert pk_aliases_path.read_text() == "# aliases stub"
    assert icon_path.read_text() == "# icon stub"

    desktop_content = desktop_file.read_text()
    assert f"Exec={venv_dir}/bin/python {autostart_script_path}" in desktop_content
    assert f"Icon={icon_path}" in desktop_content

    shortcut_content = desktop_shortcut.read_text()
    assert f"Exec={venv_dir}/bin/python {autostart_script_path}" in shortcut_content
    assert f"Icon={icon_path}" in shortcut_content
    assert desktop_shortcut.stat().st_mode & 0o111 == 0o111
    assert "quick_exec=1" in libfm_conf.read_text()

    assert "# >>> deskpi-karaoke aliases >>>" in (home / ".bashrc").read_text()
    assert "# >>> deskpi-karaoke aliases >>>" in (home / ".zshrc").read_text()


def test_remove_legacy_desktop_shortcuts_only_removes_pikaraoke_files(
    tmp_path, monkeypatch
):
    desktop_dir = tmp_path / "Desktop"
    desktop_dir.mkdir()
    legacy_start = desktop_dir / "start_pikaraoke.desktop"
    legacy_start.write_text("Exec=lxterminal -e pikaraoke\n")
    # same legacy name but not ours -> must survive
    unrelated = desktop_dir / "UpgradePikaraoke.desktop"
    unrelated.write_text("Exec=something-else\n")
    current = desktop_dir / "Start PiKaraoke.desktop"
    current.write_text("Exec=pikaraoke\n")
    monkeypatch.setattr(assets.constants, "DESKTOP_DIR", desktop_dir)

    assets.remove_legacy_desktop_shortcuts()
    assets.remove_legacy_desktop_shortcuts()  # idempotent on a clean desktop

    assert not legacy_start.exists()
    assert unrelated.exists()
    assert current.exists()
