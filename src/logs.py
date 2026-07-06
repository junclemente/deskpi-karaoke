"""System log rotation for the long-running pikaraoke subprocess's output.

The autostart launcher redirects the pikaraoke subprocess's stdout/stderr
directly into a file via subprocess.Popen(stdout=log, ...); Python's own
logging.RotatingFileHandler can't rotate a file a *different* process is
writing to via an inherited file descriptor. System `logrotate` with
`copytruncate` is the standard tool for exactly this situation.
"""

import logging
import tempfile
from pathlib import Path

from src import constants
from src.shell import log_section, run

logger = logging.getLogger(__name__)

LOGROTATE_TARGET = Path("/etc/logrotate.d/pikaraoke")


def _logrotate_config_content() -> str:
    return f"""{constants.HOME}/pikaraoke_output.log
{constants.HOME}/pikaraoke_launcher.log
{{
    size 5M
    rotate 3
    copytruncate
    missingok
    notifempty
    compress
    delaycompress
}}
"""


def install_logrotate_config():
    log_section("Configuring log rotation")
    content = _logrotate_config_content()
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".conf") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        run(["sudo", "cp", tmp_path, str(LOGROTATE_TARGET)])
        run(["sudo", "chmod", "644", str(LOGROTATE_TARGET)])
        logger.info("✅ Wrote %s", LOGROTATE_TARGET)
    except Exception as e:
        logger.warning("⚠️  Could not configure logrotate: %s", e)
    finally:
        Path(tmp_path).unlink(missing_ok=True)
