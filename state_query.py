#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Read/write a single field in ~/.deskpi-karaoke/state.toml.

Used by the bash `pk_aliases` helper, which has no TOML parser of its own:
    python3 state_query.py get version
    python3 state_query.py get last_applied_sha_dev unknown
    python3 state_query.py set last_applied_sha_dev abc123
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.state import load_state, save_state  # noqa: E402


def main():
    if len(sys.argv) < 3:
        print(
            "Usage: state_query.py get <key> [default] | set <key> <value>",
            file=sys.stderr,
        )
        sys.exit(1)

    action, key = sys.argv[1], sys.argv[2]

    if action == "get":
        default = sys.argv[3] if len(sys.argv) > 3 else ""
        value = load_state().get(key, default)
        print(value)
    elif action == "set":
        if len(sys.argv) < 4:
            print("Usage: state_query.py set <key> <value>", file=sys.stderr)
            sys.exit(1)
        save_state({key: sys.argv[3]})
    else:
        print(f"Unknown action: {action!r} (expected 'get' or 'set')", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
