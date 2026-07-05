"""Git introspection and installer state recording under ~/.deskpi-karaoke."""

from typing import Optional

from src.constants import REPO_ROOT, STATE_DIR
from src.shell import print_h, run


def git(cmd: str, default: Optional[str] = None) -> Optional[str]:
    try:
        out = run(
            ["git"] + cmd.split(), check=True, cwd=str(REPO_ROOT), capture_output=True
        ).stdout.strip()
        return out
    except Exception:
        return default


def record_state():
    print_h("Recording installer state")
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    branch = git("rev-parse --abbrev-ref HEAD", default="unknown") or "unknown"
    if branch in ("dev", "develop"):
        sha = git("rev-parse HEAD", default="") or ""
        if sha:
            (STATE_DIR / ".last_applied_sha_dev").write_text(sha + "\n")
            print(f"dev branch detected; recorded SHA {sha}")
    else:
        tag = git("describe --tags --abbrev=0", default="") or ""
        if tag:
            (STATE_DIR / "VERSION").write_text(tag + "\n")
            print(f"main/tagged install; recorded VERSION {tag}")
        else:
            # fallback — still write something so pk update logic has a file
            (STATE_DIR / "VERSION").write_text("0.0.0\n")
            print("No tag found; wrote VERSION 0.0.0")
