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


def test_record_state_dev_branch_writes_sha_file(tmp_path, monkeypatch):
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

    sha_file = state_dir / ".last_applied_sha_dev"
    assert sha_file.read_text() == "deadbeef\n"
    assert not (state_dir / "VERSION").exists()


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

    assert (state_dir / "VERSION").read_text() == "v1.2.3\n"
    assert not (state_dir / ".last_applied_sha_dev").exists()


def test_record_state_main_branch_no_tag_writes_fallback_version(tmp_path, monkeypatch):
    state_dir = tmp_path / ".deskpi-karaoke"
    monkeypatch.setattr(state.constants, "STATE_DIR", state_dir)

    def fake_git(cmd, default=None):
        if cmd.startswith("rev-parse --abbrev-ref"):
            return "main"
        return default or ""

    monkeypatch.setattr(state, "git", fake_git)

    state.record_state()

    assert (state_dir / "VERSION").read_text() == "0.0.0\n"
