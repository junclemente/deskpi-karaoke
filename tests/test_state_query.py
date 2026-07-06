import os
import subprocess
import sys
from pathlib import Path

STATE_QUERY = Path(__file__).resolve().parent.parent / "state_query.py"


def _run(args, home):
    env = {**os.environ, "HOME": str(home)}
    return subprocess.run(
        [sys.executable, str(STATE_QUERY)] + args,
        env=env,
        capture_output=True,
        text=True,
    )


def test_get_returns_default_when_state_file_missing(tmp_path):
    result = _run(["get", "version", "unknown"], tmp_path)

    assert result.returncode == 0
    assert result.stdout.strip() == "unknown"


def test_set_then_get_round_trips(tmp_path):
    set_result = _run(["set", "version", "v1.2.3"], tmp_path)
    assert set_result.returncode == 0

    get_result = _run(["get", "version"], tmp_path)
    assert get_result.stdout.strip() == "v1.2.3"

    state_file = tmp_path / ".deskpi-karaoke" / "state.toml"
    assert state_file.exists()
    assert 'version = "v1.2.3"' in state_file.read_text()


def test_unknown_action_exits_nonzero(tmp_path):
    result = _run(["frobnicate", "version"], tmp_path)

    assert result.returncode != 0
