from unittest.mock import Mock

from src import deskpi


def test_is_pi4_true_when_model_matches(monkeypatch):
    monkeypatch.setattr(
        deskpi.Path, "read_text", lambda self: "Raspberry Pi 4 Model B Rev 1.4"
    )
    assert deskpi._is_pi4() is True


def test_is_pi4_false_on_other_hardware(monkeypatch):
    monkeypatch.setattr(
        deskpi.Path, "read_text", lambda self: "Raspberry Pi 5 Model B Rev 1.0"
    )
    assert deskpi._is_pi4() is False


def test_is_pi4_false_when_file_missing(monkeypatch):
    def raise_not_found(self):
        raise FileNotFoundError()

    monkeypatch.setattr(deskpi.Path, "read_text", raise_not_found)
    assert deskpi._is_pi4() is False


def test_skips_when_not_pi4(monkeypatch, caplog):
    monkeypatch.setattr(deskpi, "_is_pi4", lambda: False)
    fake_run = Mock()
    monkeypatch.setattr(deskpi, "run", fake_run)

    with caplog.at_level("WARNING", logger="src.deskpi"):
        result = deskpi.install_deskpi_drivers()

    assert result is False
    assert "for Pi 4 only" in caplog.text
    fake_run.assert_not_called()


def test_skips_when_already_installed(monkeypatch, caplog):
    monkeypatch.setattr(deskpi, "_is_pi4", lambda: True)
    monkeypatch.setattr(deskpi, "_already_installed", lambda: True)
    fake_run = Mock()
    monkeypatch.setattr(deskpi, "run", fake_run)

    with caplog.at_level("INFO", logger="src.deskpi"):
        result = deskpi.install_deskpi_drivers()

    assert result is False
    assert "already installed" in caplog.text
    fake_run.assert_not_called()


def test_installs_and_cleans_up_when_missing(monkeypatch, tmp_path):
    monkeypatch.setattr(deskpi, "_is_pi4", lambda: True)
    monkeypatch.setattr(deskpi, "_already_installed", lambda: False)
    monkeypatch.setattr(deskpi.tempfile, "mkdtemp", lambda prefix="": str(tmp_path))
    fake_run = Mock()
    monkeypatch.setattr(deskpi, "run", fake_run)

    result = deskpi.install_deskpi_drivers()

    assert result is True
    assert fake_run.call_count == 2
    clone_call, install_call = fake_run.call_args_list
    assert clone_call.args[0][:2] == ["git", "clone"]
    assert deskpi.DESKPI_REPO_URL in clone_call.args[0]
    assert str(tmp_path) in install_call.args[0]
    # the temp clone dir itself should be cleaned up afterward
    assert not tmp_path.exists()
