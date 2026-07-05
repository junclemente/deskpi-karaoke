from unittest.mock import Mock

from src import logs


def test_logrotate_config_content_targets_both_log_files(monkeypatch, tmp_path):
    monkeypatch.setattr(logs.constants, "HOME", tmp_path)

    content = logs._logrotate_config_content()

    assert f"{tmp_path}/pikaraoke_output.log" in content
    assert f"{tmp_path}/pikaraoke_launcher.log" in content
    assert "copytruncate" in content
    assert "rotate 3" in content


def test_install_logrotate_config_copies_and_chmods(monkeypatch, tmp_path):
    monkeypatch.setattr(logs.constants, "HOME", tmp_path)
    fake_run = Mock()
    monkeypatch.setattr(logs, "run", fake_run)

    logs.install_logrotate_config()

    assert fake_run.call_count == 2
    cp_call, chmod_call = fake_run.call_args_list
    assert cp_call.args[0][:2] == ["sudo", "cp"]
    assert cp_call.args[0][2].endswith(".conf")
    assert cp_call.args[0][3] == str(logs.LOGROTATE_TARGET)
    assert chmod_call.args[0] == ["sudo", "chmod", "644", str(logs.LOGROTATE_TARGET)]


def test_install_logrotate_config_survives_run_failure(monkeypatch, tmp_path, caplog):
    monkeypatch.setattr(logs.constants, "HOME", tmp_path)

    def raise_error(*a, **k):
        raise RuntimeError("no sudo")

    monkeypatch.setattr(logs, "run", raise_error)

    with caplog.at_level("WARNING", logger="src.logs"):
        logs.install_logrotate_config()  # should not raise

    assert "Could not configure logrotate" in caplog.text
