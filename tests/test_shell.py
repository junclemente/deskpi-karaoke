from unittest.mock import Mock

from src import shell


def test_log_section_wraps_message(caplog):
    with caplog.at_level("INFO", logger="src.shell"):
        shell.log_section("Hello")
    assert "=== Hello ===" in caplog.text


def test_run_with_string_command_uses_shell_true(monkeypatch):
    fake_run = Mock(return_value="ok")
    monkeypatch.setattr(shell.subprocess, "run", fake_run)

    shell.run("echo hi", check=False)

    fake_run.assert_called_once_with(
        "echo hi",
        check=False,
        cwd=None,
        env=None,
        capture_output=False,
        text=True,
        shell=True,
    )


def test_run_with_list_command_does_not_use_shell(monkeypatch):
    fake_run = Mock(return_value="ok")
    monkeypatch.setattr(shell.subprocess, "run", fake_run)

    shell.run(["echo", "hi"], check=True)

    fake_run.assert_called_once_with(
        ["echo", "hi"], check=True, cwd=None, env=None, capture_output=False, text=True
    )
    # list-form calls must never pass shell=True
    assert "shell" not in fake_run.call_args.kwargs


def test_safe_remove_deletes_file(tmp_path):
    f = tmp_path / "file.txt"
    f.write_text("data")

    shell.safe_remove(f)

    assert not f.exists()


def test_safe_remove_deletes_directory(tmp_path):
    d = tmp_path / "somedir"
    d.mkdir()
    (d / "inner.txt").write_text("data")

    shell.safe_remove(d)

    assert not d.exists()


def test_safe_remove_skips_pikaraoke_songs_folder(tmp_path):
    d = tmp_path / "pikaraoke-songs"
    d.mkdir()
    (d / "song.mp4").write_text("data")

    shell.safe_remove(d)

    assert d.exists()
    assert (d / "song.mp4").exists()


def test_safe_remove_noop_on_missing_path(tmp_path):
    missing = tmp_path / "does-not-exist"
    # Should not raise
    shell.safe_remove(missing)


def test_stop_service_stops_and_disables(monkeypatch):
    fake_run = Mock()
    monkeypatch.setattr(shell.subprocess, "run", fake_run)

    shell.stop_service("deskpi.service")

    assert fake_run.call_count == 2
    fake_run.assert_any_call(
        ["sudo", "systemctl", "stop", "deskpi.service"], check=False
    )
    fake_run.assert_any_call(
        ["sudo", "systemctl", "disable", "deskpi.service"], check=False
    )
