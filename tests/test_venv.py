from unittest.mock import Mock

from src import venv


def test_ensure_venv_creates_when_missing(tmp_path, monkeypatch):
    venv_dir = tmp_path / ".venv-pikaraoke"
    monkeypatch.setattr(venv.constants, "VENV_DIR", venv_dir)
    fake_run = Mock()
    monkeypatch.setattr(venv, "run", fake_run)

    result = venv.ensure_venv()

    assert fake_run.call_count == 2
    create_call, pip_call = fake_run.call_args_list
    assert create_call.args[0] == [venv.sys.executable, "-m", "venv", str(venv_dir)]
    assert str(venv_dir / "bin" / "python") in pip_call.args[0][0]
    assert result == venv_dir / "bin" / "python"


def test_ensure_venv_skips_creation_when_present(tmp_path, monkeypatch):
    venv_dir = tmp_path / ".venv-pikaraoke"
    venv_dir.mkdir()
    monkeypatch.setattr(venv.constants, "VENV_DIR", venv_dir)
    fake_run = Mock()
    monkeypatch.setattr(venv, "run", fake_run)

    venv.ensure_venv()

    # Only the pip upgrade call, no venv-creation call
    assert fake_run.call_count == 1
    (pip_call,) = fake_run.call_args_list
    assert "pip" in pip_call.args[0]
