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


def test_copy_assets_copies_files_and_writes_desktop_entry(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "autostart_pikaraoke.py").write_text("# autostart stub")
    (assets_dir / "pikaraoke_ui.py").write_text("# ui stub")
    (assets_dir / "state_toml.py").write_text("# state_toml stub")
    (assets_dir / "pk_aliases").write_text("# aliases stub")

    venv_dir = home / ".venv-pikaraoke"
    autostart_dir = home / ".config" / "autostart"
    desktop_file = autostart_dir / "pikaraoke.desktop"

    monkeypatch.setattr(assets.constants, "HOME", home)
    monkeypatch.setattr(assets.constants, "ASSETS_DIR", assets_dir)
    monkeypatch.setattr(assets.constants, "VENV_DIR", venv_dir)
    monkeypatch.setattr(assets.constants, "AUTOSTART_DIR", autostart_dir)
    monkeypatch.setattr(assets.constants, "DESKTOP_FILE_PATH", desktop_file)

    assets.copy_assets()

    assert (home / "autostart_pikaraoke.py").read_text() == "# autostart stub"
    assert (home / "pikaraoke_ui.py").read_text() == "# ui stub"
    assert (home / "state_toml.py").read_text() == "# state_toml stub"
    assert (home / ".pk_aliases").read_text() == "# aliases stub"

    desktop_content = desktop_file.read_text()
    assert (
        f"Exec={venv_dir}/bin/python {home}/autostart_pikaraoke.py" in desktop_content
    )

    assert "# >>> deskpi-karaoke aliases >>>" in (home / ".bashrc").read_text()
    assert "# >>> deskpi-karaoke aliases >>>" in (home / ".zshrc").read_text()
