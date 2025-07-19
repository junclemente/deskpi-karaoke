# Changelog

All notable changes to this project will be documented in this file.

## [v0.3.0] - 2024-07-XX

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
