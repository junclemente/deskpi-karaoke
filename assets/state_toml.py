"""Tiny, dependency-free flat-TOML read/write for a `[state]` block.

Single source of truth for the flat-TOML format used by
`~/.deskpi-karaoke/state.toml`, shared by two callers that can't share a
normal Python import path:

- `src/state.py` imports this directly from the repo (`assets` is a regular
  package here).
- `assets/autostart_pikaraoke.py` is copied out to `$HOME` and run standalone
  at boot, without the repo/`src` package alongside it — `copy_assets()`
  copies this file to `$HOME` too, so it imports it as a bare same-directory
  module (`import state_toml`), same as it already does for `pikaraoke_ui`.

Stdlib only: `tomllib` (3.11+) reads TOML fine but is read-only, so writing
is hand-rolled — every value here is a plain string/bool, so a flat
`[state]` block is trivial to serialize correctly without a dependency.
"""

import tomllib
from pathlib import Path
from typing import Any


def load_state(state_file: Path) -> dict:
    """Read a flat-TOML state file, returning {} if it doesn't exist yet."""
    if not state_file.exists():
        return {}
    with state_file.open("rb") as f:
        return tomllib.load(f).get("state", {})


def _format_toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return f'"{value}"'


def save_state(state_file: Path, updates: dict) -> None:
    """Merge `updates` into the existing state and rewrite the state file."""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    data = load_state(state_file)
    data.update(updates)
    lines = ["[state]"]
    for key, value in data.items():
        lines.append(f"{key} = {_format_toml_value(value)}")
    state_file.write_text("\n".join(lines) + "\n")
