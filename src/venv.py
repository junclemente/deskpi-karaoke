"""Virtual environment creation and core package installation."""

import sys

from src.constants import PKG_CORE, VENV_DIR
from src.shell import print_h, run


def ensure_venv():
    print_h("Ensuring Python venv")
    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
    py = VENV_DIR / "bin" / "python"
    pip = [str(py), "-m", "pip"]
    run(pip + ["install", "--upgrade"] + PKG_CORE, check=False)
    return py
