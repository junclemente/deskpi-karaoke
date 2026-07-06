from unittest.mock import Mock

from src import network


def test_install_ytdlp_config_writes_expected_content(tmp_path, monkeypatch):
    cfg_dir = tmp_path / ".config" / "yt-dlp"
    monkeypatch.setattr(network.constants, "YTDLP_CONFIG_DIR", cfg_dir)

    network.install_ytdlp_config()

    cfg_file = cfg_dir / "config"
    assert cfg_file.exists()
    content = cfg_file.read_text()
    assert "--js-runtimes deno" in content
    assert "-t mp4" in content
    assert "--merge-output-format mp4" in content


def test_install_deno_skips_when_already_present(monkeypatch):
    monkeypatch.setattr(network.shutil, "which", lambda name: "/usr/bin/deno")
    fake_run = Mock()
    monkeypatch.setattr(network, "run", fake_run)

    network.install_deno()

    fake_run.assert_called_once_with(["deno", "--version"], check=False)


def test_install_deno_installs_and_patches_profile_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(network.shutil, "which", lambda name: None)
    monkeypatch.setattr(network.constants, "HOME", tmp_path)
    fake_run = Mock()
    monkeypatch.setattr(network, "run", fake_run)

    network.install_deno()

    # The curl install command should have been invoked
    curl_calls = [c for c in fake_run.call_args_list if "deno.land" in str(c.args[0])]
    assert len(curl_calls) == 1

    profile = tmp_path / ".profile"
    assert profile.exists()
    assert ".deno/bin" in profile.read_text()


def test_install_deno_does_not_duplicate_profile_path(tmp_path, monkeypatch):
    monkeypatch.setattr(network.shutil, "which", lambda name: None)
    monkeypatch.setattr(network.constants, "HOME", tmp_path)
    monkeypatch.setattr(network, "run", Mock())

    network.install_deno()
    network.install_deno()

    profile_text = (tmp_path / ".profile").read_text()
    assert profile_text.count(".deno/bin") == 1
