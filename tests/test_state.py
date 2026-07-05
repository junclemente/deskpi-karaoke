from unittest.mock import Mock

from src import state


def test_git_returns_stripped_stdout_on_success(monkeypatch):
    fake_run = Mock(return_value=Mock(stdout="  abc123\n"))
    monkeypatch.setattr(state, "run", fake_run)

    result = state.git("rev-parse HEAD")

    assert result == "abc123"


def test_git_returns_default_on_failure(monkeypatch):
    def raise_error(*args, **kwargs):
        raise RuntimeError("git not found")

    monkeypatch.setattr(state, "run", raise_error)

    result = state.git("rev-parse HEAD", default="fallback")

    assert result == "fallback"


def test_load_state_returns_empty_dict_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(state.constants, "STATE_DIR", tmp_path / ".deskpi-karaoke")

    assert state.load_state() == {}


def test_save_state_then_load_state_round_trips(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    monkeypatch.setattr(state.constants, "STATE_DIR", state_dir)

    state.save_state({"version": "v1.0.0"})
    state.save_state({"reboot_required": True})

    data = state.load_state()
    assert data["version"] == "v1.0.0"
    assert data["reboot_required"] is True

    toml_text = (state_dir / "state.toml").read_text()
    assert toml_text == ('[state]\nversion = "v1.0.0"\nreboot_required = true\n')


def test_record_state_dev_branch_writes_sha_to_state_toml(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    monkeypatch.setattr(state.constants, "STATE_DIR", state_dir)

    def fake_git(cmd, default=None):
        if cmd.startswith("rev-parse --abbrev-ref"):
            return "dev"
        if cmd.startswith("rev-parse HEAD"):
            return "deadbeef"
        return default

    monkeypatch.setattr(state, "git", fake_git)

    state.record_state()

    data = state.load_state()
    assert data["last_applied_sha_dev"] == "deadbeef"
    assert "version" not in data


def test_record_state_main_branch_with_tag_writes_version(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    monkeypatch.setattr(state.constants, "STATE_DIR", state_dir)

    def fake_git(cmd, default=None):
        if cmd.startswith("rev-parse --abbrev-ref"):
            return "main"
        if cmd.startswith("describe --tags"):
            return "v1.2.3"
        return default

    monkeypatch.setattr(state, "git", fake_git)

    state.record_state()

    data = state.load_state()
    assert data["version"] == "v1.2.3"
    assert "last_applied_sha_dev" not in data


def test_record_state_main_branch_no_tag_writes_fallback_version(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    monkeypatch.setattr(state.constants, "STATE_DIR", state_dir)

    def fake_git(cmd, default=None):
        if cmd.startswith("rev-parse --abbrev-ref"):
            return "main"
        return default or ""

    monkeypatch.setattr(state, "git", fake_git)

    state.record_state()

    assert state.load_state()["version"] == "0.0.0"


def test_record_state_removes_legacy_flat_files(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    state_dir.mkdir(parents=True)
    (state_dir / "VERSION").write_text("v0.0.1\n")
    (state_dir / ".last_applied_sha_dev").write_text("oldsha\n")
    (state_dir / "PIKARAOKE_VERSION").write_text("1.0.0\n")
    monkeypatch.setattr(state.constants, "STATE_DIR", state_dir)
    monkeypatch.setattr(state, "git", lambda cmd, default=None: default or "")

    state.record_state()

    assert not (state_dir / "VERSION").exists()
    assert not (state_dir / ".last_applied_sha_dev").exists()
    assert not (state_dir / "PIKARAOKE_VERSION").exists()
