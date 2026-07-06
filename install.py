#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PiKaraoke Installer (dev branch) — entry point.
- Idempotent
- Creates ~/.venv-pikaraoke
- Installs core packages (pikaraoke, packaging, yt-dlp)
- Copies autostart + UI helpers
- Installs pk_aliases and sources in shell rc files
- Records installer state under ~/.deskpi-karaoke

See src/cli.py for the orchestration logic and src/*.py for individual steps.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.cli import run  # noqa: E402

if __name__ == "__main__":
    run()
