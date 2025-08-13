#!/usr/bin/env python3

import argparse
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# --- Paths / Constants ---
REPO_DIR = Path(__file__).parent.resolve()
UNINSTALLER = REPO_DIR / "uninstall.py"  # legacy uninstaller (repo root)

# --- Safety: Python version ---
if sys.version_info < (3, 9):
    print("❌ Python 3.9+ is required to install PiKaraoke.")
    print(f"Detected version: {sys.version_info.major}.{sys.version_info.minor}")
    sys.exit(1)


# --- Helpers ---
def run_command(cmd, cwd=None):
    """Run a shell command and fail loudly."""
    print(f"▶️  Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def get_current_branch(repo_dir: Path) -> str | None:
    """Return current git branch, or None if not a git checkout/detached."""
    try:
        out = (
            subprocess.check_output(
                ["git", "-C", str(repo_dir), "rev-parse", "--abbrev-ref", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        return out if out and out != "HEAD" else None
    except Exception:
        return None


def get_version() -> str:
    """
    Version strategy:
      1) Latest Git tag (if repo + tags exist)
      2) If not on 'main' (or not a git checkout), treat as 'dev'
    """
    try:
        tag = (
            subprocess.check_output(
                ["git", "-C", str(REPO_DIR), "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        return tag.lstrip("v")
    except Exception:
        pass

    branch = get_current_branch(REPO_DIR)
    if branch and branch != "main":
        return "dev"
    return "dev"


def is_raspberry_pi() -> bool:
    return (
        "raspberry" in platform.uname().node.lower()
        or Path("/proc/device-tree/model").exists()
    )


def check_platform():
    print("🧠 Checking platform...")
    if not is_raspberry_pi():
        print("⚠️  Not running on Raspberry Pi. Proceeding anyway...")
    os_release = Path("/etc/os-release").read_text()
    if "bookworm" not in os_release.lower():
        print("⚠️  Warning: You are not running Raspberry Pi OS Bookworm.")


def install_system_packages():
    print("📦 Installing system packages...")
    run_command(["sudo", "apt-get", "update"])

    base = [
        "ffmpeg",
        "chromium-chromedriver",
        "git",
        "python3-venv",
        "python3-pip",
    ]
    # Try chromium-browser first, then chromium if not found
    try:
        run_command(["sudo", "apt-get", "install", "-y", "chromium-browser"] + base)
    except subprocess.CalledProcessError:
        print("⚠️  'chromium-browser' not found, trying 'chromium'...")
        run_command(["sudo", "apt-get", "install", "-y", "chromium"] + base)


def install_deskpi_drivers():
    print("🛠️ Installing DeskPi Lite 4 drivers...")
    run_command(["git", "clone", "https://github.com/DeskPi-Team/deskpi_v1.git"])
    run_command(["sudo", "./install.sh"], cwd="deskpi_v1")


def setup_virtualenv():
    print("🐍 Setting up virtual environment...")
    venv_path = Path.home() / ".venv-pikaraoke"
    if not venv_path.exists():
        run_command(["python3", "-m", "venv", str(venv_path)])
    pip = venv_path / "bin" / "pip"
    # Keep tools current & ensure yt-dlp + pikaraoke are present
    run_command([str(pip), "install", "--upgrade", "pip", "setuptools", "wheel"])
    run_command([str(pip), "install", "--upgrade", "packaging"])
    run_command([str(pip), "install", "--upgrade", "yt-dlp", "pikaraoke"])


def install_start_script():
    print("🎬 Copying start script from assets...")
    src = REPO_DIR / "assets" / "autostart_pikaraoke.py"
    dst = Path.home() / "autostart_pikaraoke.py"
    shutil.copy(src, dst)
    dst.chmod(0o755)


def install_ui_module():
    print("📁 Copying PiKaraoke UI module...")
    src = REPO_DIR / "assets" / "pikaraoke_ui.py"
    dst = Path.home() / "pikaraoke_ui.py"
    shutil.copy(src, dst)
    dst.chmod(0o644)
    print(f"✅ UI module installed at: {dst}")


def install_autostart_entry():
    print("🔁 Copying autostart entry from assets...")
    autostart_dir = Path.home() / ".config" / "autostart"
    autostart_dir.mkdir(parents=True, exist_ok=True)
    src = REPO_DIR / "assets" / "autostart_pikaraoke.desktop"
    dst = autostart_dir / "pikaraoke.desktop"
    shutil.copy(src, dst)
    dst.chmod(0o755)
    print(f"✅ Autostart file created at: {dst}")


def install_pk_aliases():
    """Copy assets/pk_aliases to ~/.pk_aliases and ensure it's sourced."""
    home = Path.home()
    pk_src = REPO_DIR / "assets" / "pk_aliases"
    pk_dst = home / ".pk_aliases"
    shutil.copy(pk_src, pk_dst)

    src_line = '[ -f "$HOME/.pk_aliases" ] && . "$HOME/.pk_aliases"'
    for rc in (home / ".bashrc", home / ".zshrc"):
        if rc.exists():
            text = rc.read_text(encoding="utf-8")
            if ".pk_aliases" not in text:
                rc.write_text(text.rstrip() + "\n" + src_line + "\n", encoding="utf-8")
    print(f"✅ Installed pk aliases from assets at: {pk_dst}")
    print("ℹ️ New terminals will load 'pk'; to use now, run: source ~/.pk_aliases")


# --- CLI ---
def parse_args():
    p = argparse.ArgumentParser(description="Install PiKaraoke on Raspberry Pi 4...")
    p.add_argument(
        "--deskpi", action="store_true", help="Install DeskPi Lite 4 drivers"
    )
    return p.parse_args()


# --- Main ---
def main():
    args = parse_args()

    # Step 0: Prepare environment/tools
    setup_virtualenv()

    # Import here after venv ensures packaging exists
    from packaging.version import Version

    version = get_version()
    print(f"\n🎤 PiKaraoke Installer v{version} Starting...\n")

    # Dev branch: skip legacy uninstall
    branch = get_current_branch(REPO_DIR)
    if branch == "dev":
        print("🧪 Dev branch detected — skipping legacy uninstall step.")
    else:
        # Only apply legacy uninstall to tagged, old versions
        if version != "dev" and Version(version) < Version("0.3.1"):
            if UNINSTALLER.exists():
                print(f"🧹 Detected < 0.3.1 — running {UNINSTALLER.name}...")
                run_command(["python3", str(UNINSTALLER)], cwd=str(REPO_DIR))
            else:
                print(
                    f"🧹 Detected < 0.3.1 but {UNINSTALLER.name} not found — skipping."
                )

    # Handle app autoupdate flag
    update_flag = Path.home() / ".pikaraoke_update_pending"
    if update_flag.exists():
        print("🔔 Update flag detected - upgrading PiKaraoke package...")
        update_flag.unlink()
        venv_bin = Path.home() / ".venv-pikaraoke" / "bin"
        pip = venv_bin / "pip"
        run_command([str(pip), "install", "--force-reinstall", "pikaraoke"])

    # System deps
    check_platform()
    install_system_packages()

    # Optional DeskPi Lite drivers
    if args.deskpi:
        install_deskpi_drivers()
    else:
        print("💡 DeskPi driver install skipped (use --deskpi to enable)")

    # Final setup
    install_start_script()
    install_autostart_entry()
    install_ui_module()
    install_pk_aliases()

    print("\n✅ Installation complete! System will automatically reboot.")
    print("🔄 Rebooting...")
    run_command(["sudo", "reboot"])


if __name__ == "__main__":
    main()
