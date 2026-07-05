"""Shared console logging setup for the installer/uninstaller CLIs."""

import logging
import sys


def setup_logging(level=logging.INFO):
    logging.basicConfig(level=level, format="%(message)s", stream=sys.stdout)
