"""Git introspection and installer state recording under
~/.deskpi-karaoke/state.toml."""

import logging
import tomllib
from typing import Any, Optional

from src import constants
from src.shell import log_section, run

logger = logging.getLogger(__name__)

STATE_FILE_NAME = "state.toml"

# Flat files this project used before consolidating into state.toml — removed
# on first run after upgrade so they don't linger as stale, misleading state.
_LEGACY_STATE_FILES = ("VERSION", ".last_applied_sha_dev", "PIKARAOKE_VERSION")


def git(cmd: str, default: Optional[str] = None) -> Optional[str]:
    try:
        out = run(
            ["git"] + cmd.split(),
            check=True,
            cwd=str(constants.REPO_ROOT),
            capture_output=True,
        ).stdout.strip()
        return out
    except Exception:
        return default


def _state_path():
    return constants.STATE_DIR / STATE_FILE_NAME


def load_state() -> dict:
    """Read ~/.deskpi-karaoke/state.toml, returning {} if it doesn't exist yet."""
    path = _state_path()
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f).get("state", {})


def _format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return f'"{value}"'


def save_state(updates: dict) -> None:
    """Merge `updates` into the existing state and rewrite state.toml.

    Hand-rolled writer instead of a library: tomllib (stdlib) is read-only,
    and every value here is a plain string/bool, so a flat [state] block is
    trivial to serialize correctly without a dependency.
    """
    constants.STATE_DIR.mkdir(parents=True, exist_ok=True)
    data = load_state()
    data.update(updates)
    lines = ["[state]"]
    for key, value in data.items():
        lines.append(f"{key} = {_format_toml_value(value)}")
    _state_path().write_text("\n".join(lines) + "\n")


def _remove_legacy_state_files():
    for name in _LEGACY_STATE_FILES:
        path = constants.STATE_DIR / name
        if path.exists():
            path.unlink()


def record_state():
    log_section("Recording installer state")
    constants.STATE_DIR.mkdir(parents=True, exist_ok=True)
    _remove_legacy_state_files()
    branch = git("rev-parse --abbrev-ref HEAD", default="unknown") or "unknown"
    if branch in ("dev", "develop"):
        sha = git("rev-parse HEAD", default="") or ""
        if sha:
            save_state({"last_applied_sha_dev": sha})
            logger.info("dev branch detected; recorded SHA %s", sha)
    else:
        tag = git("describe --tags --abbrev=0", default="") or ""
        if tag:
            save_state({"version": tag})
            logger.info("main/tagged install; recorded VERSION %s", tag)
        else:
            # fallback — still write something so pk update logic has a value
            save_state({"version": "0.0.0"})
            logger.info("No tag found; wrote VERSION 0.0.0")
