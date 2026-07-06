from src import constants


def test_py_min_loaded_from_config_toml():
    assert constants.PY_MIN == (3, 11)


def test_package_lists_loaded_from_config_toml():
    assert isinstance(constants.PKG_CORE, list) and len(constants.PKG_CORE) > 0
    assert isinstance(constants.APT_PKGS, list) and len(constants.APT_PKGS) > 0
    assert any("pikaraoke" in pkg for pkg in constants.PKG_CORE)
    assert "logrotate" in constants.APT_PKGS
