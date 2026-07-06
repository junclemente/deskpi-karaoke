from assets import state_toml


def test_load_state_returns_empty_dict_when_missing(tmp_path):
    state_file = tmp_path / "state.toml"

    assert state_toml.load_state(state_file) == {}


def test_save_state_then_load_state_round_trips(tmp_path):
    state_file = tmp_path / ".deskpi-karaoke" / "state.toml"

    state_toml.save_state(state_file, {"version": "v1.0.0"})
    state_toml.save_state(state_file, {"reboot_required": True})

    data = state_toml.load_state(state_file)
    assert data["version"] == "v1.0.0"
    assert data["reboot_required"] is True

    assert state_file.read_text() == (
        '[state]\nversion = "v1.0.0"\nreboot_required = true\n'
    )


def test_save_state_creates_parent_directory(tmp_path):
    state_file = tmp_path / "nested" / "dir" / "state.toml"

    state_toml.save_state(state_file, {"key": "value"})

    assert state_file.exists()
