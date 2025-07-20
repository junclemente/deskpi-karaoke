# Changelog

All notable changes to this project will be documented in this file.

[0.3.2] - 2024-07-18

## 📦 Version-Aware Installer + Auto-Updater

### 🚀 New Features

- 🧠 **Installer version check** using `packaging.version.Version`
- 🔁 **Auto-reinstall PiKaraoke** if major version change is detected (via `.pikaraoke_update_pending` flag)
- 💥 **Legacy cleanup**: Automatically runs `uninstall_clean.py` if previous version is `< 0.3.1`

### 🛠️ Improvements

- ✅ All `pip` installs (including `packaging`) are now safely installed inside `.venv-pikaraoke`
- 🧽 Cleaned up `install_system_packages()` to avoid global pip install conflicts (PEP 668 safe)
- 🧪 Python version check: requires **Python 3.9+** at start of install

### 📁 Refactors

- 🐍 Delayed `from packaging.version import Version` import until after venv setup to ensure compatibility
- 🔐 UI module (`pikaraoke_ui.py`) now copied to `~` for better maintainability
- 🔁 Renamed autostart script to `autostart_pikaraoke.py` for consistency

### 📝 Notes

- This version sets the foundation for future automatic update and version tracking behavior at startup.

## [0.3.1] - 2024-07-18

### 🎨 UI Enhancements

- Replaced Zenity popups with native Tkinter windows
- Info and error messages now appear at a consistent screen location
- Notifications auto-close and are non-blocking

### ⚙️ Autostart Behavior

- Improved internet detection logic
  - Polls silently for 10 seconds before showing UI
  - If no connection, notifies user and continues checking for up to 40s
- Launches PiKaraoke immediately on detection
- Graceful error message if connection fails

### 📁 Script & File Updates

- Renamed `pikaraoke_start.py` → `autostart_pikaraoke.py`
- Removed `desktop_pikaraoke_start.py` (no longer used)
- Added shared `pikaraoke_ui.py` for popups
- `.desktop` files updated to use new naming

### 🐍 System Requirements

- Assumes Python ≥ 3.9 (via Raspberry Pi OS Bookworm)

## [v0.3.0] - 2024-07-18

### 🎉 Major Features

- 🐍 **Rewrote the entire installer in Python**

  - Fully replaces the previous `install.sh` shell-based setup
  - Provides a clean, structured foundation for future enhancements

- 💻 **Single-command setup with `install.py`**

  - Optional `--deskpi` flag installs DeskPi Lite 4 drivers
  - Installs system dependencies: `ffmpeg`, `chromium-browser`, `python3-venv`, etc.
  - Creates Python virtual environment at `~/.venv-pikaraoke`

- 🔁 **Autostart after internet is detected**

  - On boot, the system waits up to 30 seconds for internet before launching PiKaraoke
  - Internet-aware logic handled via `pikaraoke_start.py`
  - No RaspiWiFi fallback or reboots required

- 📂 **Assets-based setup**

  - Copies `pikaraoke_start.py` and autostart `.desktop` file from the `assets/` folder
  - Improves maintainability and decouples logic from code

- 🧹 **Two new uninstallers**
  - `uninstall.py`: Removes current (v0.3.0+) install cleanly
  - `uninstall_clean.py`: Wipes legacy installs while preserving the `pikaraoke-songs` folder
  - Both support `--deskpi` to optionally remove DeskPi drivers

### 🔧 Cleanups & Internal Changes

- 🚫 Removed all legacy `.sh` scripts and `scripts/` folder
- 🧼 Simplified startup handling — no need for `.bashrc`, `cron`, or `systemd`
- 🗃️ Project structure standardized for future testing and linting
- 📃 Updated `README.md` to reflect the Python-first workflow

---

### ✅ Recommended for:

- Fresh installs on Raspberry Pi 4 running Raspberry Pi OS (Bookworm Desktop)
- Anyone who previously installed PiKaraoke via shell script
- Users who want a clean, auto-starting setup with minimal setup time

---

## [v0.2.0] - 2025-07-16

### Added

- Autostart script waits for Wi-Fi before launching PiKaraoke
- Zenity popups to inform the user
- Wi-Fi GUI opens if no connection is found
- Desktop autostart integration

### Changed

- install.sh now copies the launcher script instead of embedding it

### Removed

- CI ShellCheck linting step (temporarily)

### Fixed

- Git pull conflict on install.sh due to chmod
- ShellCheck false-positive for `source`
