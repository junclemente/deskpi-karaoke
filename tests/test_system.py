from unittest.mock import Mock, mock_open

import pytest

from src import system


def test_ensure_python_version_passes_when_high_enough(monkeypatch):
    monkeypatch.setattr(system.sys, "version_info", (3, 12, 0))
    monkeypatch.setattr(system.constants, "PY_MIN", (3, 10))

    system.ensure_python_version()  # should not raise


def test_ensure_python_version_raises_when_too_old(monkeypatch):
    monkeypatch.setattr(system.sys, "version_info", (3, 9, 0))
    monkeypatch.setattr(system.constants, "PY_MIN", (3, 10))

    with pytest.raises(SystemExit):
        system.ensure_python_version()


def test_check_platform_recognizes_bookworm_pi(monkeypatch, capsys):
    fake_uname = Mock(system="Linux", release="6.1.0", machine="aarch64")
    monkeypatch.setattr(system.platform, "uname", lambda: fake_uname)
    # machine alone doesn't say "raspberry" - osrel needs to mention it
    monkeypatch.setattr(
        "builtins.open",
        mock_open(read_data="ID=debian\nVERSION_CODENAME=bookworm\nraspberry pi\n"),
    )

    system.check_platform()

    out = capsys.readouterr().out
    assert "Non-Bookworm" not in out
    assert "does not appear to be a Raspberry Pi" not in out


def test_check_platform_warns_on_non_bookworm_non_pi(monkeypatch, capsys):
    fake_uname = Mock(system="Linux", release="6.8.0", machine="x86_64")
    monkeypatch.setattr(system.platform, "uname", lambda: fake_uname)

    def raise_not_found(*args, **kwargs):
        raise FileNotFoundError("no such file")

    monkeypatch.setattr("builtins.open", raise_not_found)

    system.check_platform()

    out = capsys.readouterr().out
    assert "Non-Bookworm OS detected" in out
    assert "does not appear to be a Raspberry Pi" in out


def test_apt_install_skips_when_apt_missing(monkeypatch):
    monkeypatch.setattr(system.shutil, "which", lambda name: None)
    fake_run = Mock()
    monkeypatch.setattr(system, "run", fake_run)

    system.apt_install()

    fake_run.assert_not_called()


def test_apt_install_uses_sudo_when_available(monkeypatch):
    def fake_which(name):
        return {"apt-get": "/usr/bin/apt-get", "sudo": "/usr/bin/sudo"}.get(name)

    monkeypatch.setattr(system.shutil, "which", fake_which)
    fake_run = Mock()
    monkeypatch.setattr(system, "run", fake_run)

    system.apt_install()

    assert fake_run.call_count == 3
    for call in fake_run.call_args_list:
        cmd = call.args[0]
        assert cmd.startswith("/usr/bin/sudo /usr/bin/apt-get")


def test_apt_install_without_sudo(monkeypatch):
    def fake_which(name):
        return "/usr/bin/apt-get" if name == "apt-get" else None

    monkeypatch.setattr(system.shutil, "which", fake_which)
    fake_run = Mock()
    monkeypatch.setattr(system, "run", fake_run)

    system.apt_install()

    assert fake_run.call_count == 3
    for call in fake_run.call_args_list:
        cmd = call.args[0]
        assert "sudo" not in cmd
