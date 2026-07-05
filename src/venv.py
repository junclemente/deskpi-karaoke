"""Virtual environment creation and core package installation."""

import sys

from src import constants
from src.shell import print_h, run


def ensure_venv():
    print_h("Ensuring Python venv")
    if not constants.VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(constants.VENV_DIR)])
    py = constants.VENV_DIR / "bin" / "python"
    pip = [str(py), "-m", "pip"]
    run(pip + ["install", "--upgrade"] + constants.PKG_CORE, check=False)
    return py
