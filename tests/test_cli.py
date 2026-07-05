from unittest.mock import Mock

import pytest

from src import cli


def test_run_calls_main_and_exits_cleanly(monkeypatch):
    fake_main = Mock()
    monkeypatch.setattr(cli, "main", fake_main)

    cli.run()

    fake_main.assert_called_once()


def test_run_maps_keyboard_interrupt_to_exit_130(monkeypatch):
    def raise_interrupt():
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli, "main", raise_interrupt)

    with pytest.raises(SystemExit) as exc_info:
        cli.run()

    assert exc_info.value.code == 130


def test_run_propagates_system_exit_unchanged(monkeypatch):
    def raise_system_exit():
        raise SystemExit(42)

    monkeypatch.setattr(cli, "main", raise_system_exit)

    with pytest.raises(SystemExit) as exc_info:
        cli.run()

    assert exc_info.value.code == 42


def test_run_maps_generic_exception_to_exit_1(monkeypatch):
    def raise_error():
        raise ValueError("boom")

    monkeypatch.setattr(cli, "main", raise_error)

    with pytest.raises(SystemExit) as exc_info:
        cli.run()

    assert exc_info.value.code == 1


def test_main_calls_steps_in_documented_order(monkeypatch):
    calls = []

    def tracker(name):
        return lambda *a, **k: calls.append(name)

    monkeypatch.setattr(cli, "ensure_python_version", tracker("ensure_python_version"))
    monkeypatch.setattr(cli, "check_platform", tracker("check_platform"))
    monkeypatch.setattr(cli, "apt_install", tracker("apt_install"))
    monkeypatch.setattr(cli, "install_deno", tracker("install_deno"))
    monkeypatch.setattr(cli, "ensure_venv", tracker("ensure_venv"))
    monkeypatch.setattr(cli, "install_ytdlp_config", tracker("install_ytdlp_config"))
    monkeypatch.setattr(cli, "copy_assets", tracker("copy_assets"))
    monkeypatch.setattr(cli, "record_state", tracker("record_state"))

    cli.main()

    assert calls == [
        "ensure_python_version",
        "check_platform",
        "apt_install",
        "install_deno",
        "ensure_venv",
        "install_ytdlp_config",
        "copy_assets",
        "record_state",
    ]
