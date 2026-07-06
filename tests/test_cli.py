import argparse
from unittest.mock import Mock

import pytest

from src import cli


def _fake_args(deskpi=False):
    return argparse.Namespace(deskpi=deskpi)


def test_run_calls_main_and_exits_cleanly(monkeypatch):
    monkeypatch.setattr(cli, "parse_args", lambda: _fake_args())
    fake_main = Mock()
    monkeypatch.setattr(cli, "main", fake_main)

    cli.run()

    fake_main.assert_called_once_with(_fake_args())


def test_run_maps_keyboard_interrupt_to_exit_130(monkeypatch):
    monkeypatch.setattr(cli, "parse_args", lambda: _fake_args())

    def raise_interrupt(args):
        raise KeyboardInterrupt()

    monkeypatch.setattr(cli, "main", raise_interrupt)

    with pytest.raises(SystemExit) as exc_info:
        cli.run()

    assert exc_info.value.code == 130


def test_run_propagates_system_exit_unchanged(monkeypatch):
    monkeypatch.setattr(cli, "parse_args", lambda: _fake_args())

    def raise_system_exit(args):
        raise SystemExit(42)

    monkeypatch.setattr(cli, "main", raise_system_exit)

    with pytest.raises(SystemExit) as exc_info:
        cli.run()

    assert exc_info.value.code == 42


def test_run_maps_generic_exception_to_exit_1(monkeypatch):
    monkeypatch.setattr(cli, "parse_args", lambda: _fake_args())

    def raise_error(args):
        raise ValueError("boom")

    monkeypatch.setattr(cli, "main", raise_error)

    with pytest.raises(SystemExit) as exc_info:
        cli.run()

    assert exc_info.value.code == 1


def test_main_calls_steps_in_documented_order_without_deskpi(monkeypatch):
    calls = []

    def tracker(name):
        return lambda *a, **k: calls.append(name)

    monkeypatch.setattr(cli, "ensure_python_version", tracker("ensure_python_version"))
    monkeypatch.setattr(cli, "check_platform", tracker("check_platform"))
    monkeypatch.setattr(cli, "apt_install", tracker("apt_install"))
    monkeypatch.setattr(cli, "install_deno", tracker("install_deno"))
    monkeypatch.setattr(cli, "ensure_venv", tracker("ensure_venv"))
    monkeypatch.setattr(cli, "install_ytdlp_config", tracker("install_ytdlp_config"))
    monkeypatch.setattr(
        cli, "install_logrotate_config", tracker("install_logrotate_config")
    )
    monkeypatch.setattr(cli, "copy_assets", tracker("copy_assets"))
    monkeypatch.setattr(cli, "record_state", tracker("record_state"))
    fake_install_deskpi = Mock()
    fake_save_state = Mock()
    monkeypatch.setattr(cli, "install_deskpi_drivers", fake_install_deskpi)
    monkeypatch.setattr(cli, "save_state", fake_save_state)

    cli.main(_fake_args(deskpi=False))

    assert calls == [
        "ensure_python_version",
        "check_platform",
        "apt_install",
        "install_deno",
        "ensure_venv",
        "install_ytdlp_config",
        "install_logrotate_config",
        "copy_assets",
        "record_state",
    ]
    fake_install_deskpi.assert_not_called()
    fake_save_state.assert_not_called()


def test_main_installs_deskpi_drivers_and_records_reboot_state(monkeypatch):
    for name in (
        "ensure_python_version",
        "check_platform",
        "apt_install",
        "install_deno",
        "ensure_venv",
        "install_ytdlp_config",
        "install_logrotate_config",
        "copy_assets",
        "record_state",
    ):
        monkeypatch.setattr(cli, name, Mock())

    fake_install_deskpi = Mock(return_value=True)
    fake_save_state = Mock()
    monkeypatch.setattr(cli, "install_deskpi_drivers", fake_install_deskpi)
    monkeypatch.setattr(cli, "save_state", fake_save_state)

    cli.main(_fake_args(deskpi=True))

    fake_install_deskpi.assert_called_once()
    fake_save_state.assert_called_once_with({"reboot_required": True})
