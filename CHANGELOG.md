# Changelog

All notable changes to this project will be documented in this file.

## [v0.7.0] - 2026-07-06

### 🐛 Fixes

- **`uninstall.py`/`uninstall_clean.py` actually uninstall PiKaraoke now.**
  Both scripts had drifted out of sync with the current install scheme and
  only cleaned up paths from a much older, pre-TOML-migration layout.
  Concretely, **neither script removed `~/.config/autostart/pikaraoke.desktop`
  — the actual autostart entry `copy_assets()` writes** — they instead
  targeted `/etc/xdg/autostart/pikaraoke.desktop`, a system-wide path
  nothing has created since that older scheme. Running `uninstall.py` did
  not stop PiKaraoke from auto-launching on the next reboot.
  - Also newly cleaned up: `~/autostart_pikaraoke.py`, `~/pikaraoke_ui.py`,
    `~/state_toml.py`, `~/pikaraoke_icon.png` (the copied helper
    scripts/icon), `~/.pk_aliases` plus its sourced block in `.bashrc`/
    `.zshrc` (via a new `src/assets.remove_rc_block()`, the reverse of
    `ensure_rc_sourced()`), `~/.deskpi-karaoke/` (installer state), and
    `~/.config/yt-dlp/` (yt-dlp defaults).
  - `uninstall_clean.py` keeps sweeping the legacy `/etc/xdg/...` path too
    (via the new `constants.LEGACY_XDG_AUTOSTART_PATH`), since that's
    exactly its job — a thorough sweep for older installs — while
    `uninstall.py` now targets only the current scheme.
- **Root cause:** these paths were hardcoded independently in each
  uninstaller rather than referencing `src/constants.py`, so they silently
  fell out of sync as `install.py` evolved. `src/constants.py` gained
  `AUTOSTART_SCRIPT_PATH`, `PIKARAOKE_UI_PATH`, `STATE_TOML_HELPER_PATH`,
  `PK_ALIASES_PATH`, `YTDLP_CONFIG_DIR`, and `LEGACY_XDG_AUTOSTART_PATH`;
  `src/assets.py` and `src/network.py` now reference these same constants
  instead of inlining the paths a second time, so uninstall and install
  can no longer drift apart the same way again.
- **This drift went unnoticed because neither uninstaller had any test
  coverage.** Added `tests/test_uninstall.py` and
  `tests/test_uninstall_clean.py` (21 new tests, plus 4 more covering
  `remove_rc_block()` in `tests/test_assets.py`), including explicit
  regression tests reproducing the exact bug (asserting the *current*
  autostart path is removed, not the legacy one).

## [v0.6.6] - 2026-07-06

### 🚀 New Features

- **Both `.desktop` entries now use the actual PiKaraoke mascot icon**
  instead of the generic `utilities-terminal` console icon. The icon
  (`assets/pikaraoke_icon.png`) was extracted from the installed
  `pikaraoke` package's own `static/images/logo.png` banner — isolated via
  connected-component analysis (not a manual crop guess) to cleanly pull
  out just the mascot, excluding the "PiKaraoke" wordmark and music-note
  glyphs sharing that image, then padded to a square and downsampled to
  256×256 with a transparent background.
  - `src/constants.py` gained `ICON_PATH` (`~/pikaraoke_icon.png`).
  - `src/assets.py`'s `copy_assets()` now copies the icon alongside the
    other assets and both `.desktop` entries' `Icon=` line points at it.
  - Verified end-to-end: ran `copy_assets()` for real and confirmed both
    `~/Desktop/Start PiKaraoke.desktop` and
    `~/.config/autostart/pikaraoke.desktop` reference the installed icon
    path, and the copied PNG is a valid 256×256 RGBA image.

## [v0.6.5] - 2026-07-06

### 🐛 Fixes

- **The real fix for the desktop icon's "Execute / Execute in Terminal /
  Open / Cancel" prompt** — v0.6.4's `gio set metadata::trusted` was based
  on a wrong assumption (that's a GNOME/Nautilus convention) and confirmed
  not to work on Raspberry Pi OS's PCManFM even after `pk devupdate` +
  reboot. Traced the actual gate through libfm's source
  (`fm-gtk-file-launcher.c`'s `on_exec_file()`): the dialog is skipped only
  when `fm_config->quick_exec` is true, which maps to `quick_exec=1` under
  `[config]` in `~/.config/libfm/libfm.conf` — the same setting toggled by
  PCManFM's Edit → Preferences → "Don't ask options on launch executable
  file" checkbox.
  - `src/constants.py` gained `LIBFM_CONFIG_PATH`.
  - `src/assets.py`'s new `enable_quick_exec()` replaces the removed
    `mark_desktop_file_trusted()`, read-modify-writing `libfm.conf` via
    `configparser.RawConfigParser` (raw, not interpolating, so existing
    `%`-bearing values like `terminal=lxterminal -e %s` survive intact) —
    idempotent, preserves any other sections/keys already in the file,
    creates it if missing.
  - Verified directly against a simulated existing `libfm.conf` (with a
    `%s`-bearing `terminal=` line) and a fresh one with none: both come out
    with every prior setting intact plus `quick_exec=1` added exactly once.

## [v0.6.4] - 2026-07-06

### 🐛 Fixes

- **Desktop icon no longer prompts "Execute / Execute in Terminal / Open /
  Cancel" on double-click.** PCManFM (Raspberry Pi OS's file manager) treats
  a `.desktop` file as an untrusted script — regardless of its executable
  bit — until its GIO `metadata::trusted` attribute is set to `yes`.
  `src/assets.py`'s `copy_assets()` now calls `gio set <path>
  metadata::trusted yes` on `~/Desktop/Start PiKaraoke.desktop` right after
  `chmod`, via a new `mark_desktop_file_trusted()` helper (silently
  skipped if `gio` isn't available). Verified directly: after `gio set`,
  `gio info -a metadata::trusted` reports `yes` on the shortcut.

## [v0.6.3] - 2026-07-06

### 🐛 Fixes

- **Removed the `pikaraoke==1.18.0` pin entirely.** The splash-screen crash
  it worked around (`get_raspi_wifi_text()` missing a required `url`
  argument) was caused by an abandoned raspi-portal integration attempt,
  not by a bug in pikaraoke itself — the premise behind the pin (and the
  v0.6.2 pin-tracking machinery built to respect it) no longer holds now
  that raspi-portal integration isn't in use. `config.toml`'s core package
  list now installs plain `pikaraoke` (unpinned), and
  `PIKARAOKE_PIN`/`state.toml`'s `pikaraoke_pin`/`autostart_pikaraoke.py`'s
  pin-targeting branch from v0.6.2 are reverted — installs and boot-time
  updates track pikaraoke's latest PyPI release again, as before v0.4.2.
- Verified the fix against a venv still holding the old pinned state
  (`pikaraoke 1.18.0` + `Flask 2.2.5`, the exact combination that produced
  pip's "dependency conflicts... flask-smorest requires flask<4,>=3.0.2"
  warning during install): re-running the installer's package-install step
  now upgrades cleanly to `pikaraoke 1.19.0` + `Flask 3.1.2` +
  `flask-smorest 0.47.0` with no resolver warnings, confirmed via
  `pip check` (`No broken requirements found.`).

## [v0.6.2] - 2026-07-06

### 🐛 Fixes

- **Autostart's update check no longer overrides the `config.toml` pikaraoke
  pin.** `pikaraoke==1.18.0` is pinned there because 1.19.0 has a breaking
  splash-screen bug, but `assets/autostart_pikaraoke.py`'s `check_and_update()`
  ignored that pin and always chased PyPI's absolute latest release. That let
  the buggy 1.19.0 (plus its `flask>=3.1.0`/`flask-smorest` deps) get silently
  installed on boot, only for the next `install.py`/`pk update`/`pk devupdate`
  run to force it back down to 1.18.0 — downgrading Flask along with it and
  leaving `flask-smorest` orphaned with an incompatible Flask, which is what
  produced pip's "dependency conflicts" warning during install.
  - `src/constants.py` now parses `PIKARAOKE_PIN` out of `config.toml`'s
    `pikaraoke==X.Y.Z` core-package entry.
  - `src/state.py`'s `record_state()` writes it to `state.toml` as
    `pikaraoke_pin` on every install.
  - `autostart_pikaraoke.py`'s `check_and_update()` now targets that pin
    directly (upgrading *or* downgrading to match it) instead of querying
    PyPI, when one is recorded; falls back to the old latest-chasing
    behavior only if no pin is present.

## [v0.6.1] - 2026-07-06

### 🚀 New Features

- **Restored the `~/Desktop/Start PiKaraoke.desktop` clickable icon.**
  `uninstall.py`/`uninstall_clean.py` already cleaned this path up as a
  legacy artifact, but nothing on `dev`/`main` created it — `install.py`
  only wrote the `~/.config/autostart` entry. `src/assets.py`'s
  `copy_assets()` now also writes this desktop shortcut (reusing the same
  `~/autostart_pikaraoke.py` launcher as autostart, so internet-wait,
  update-check, and logging behave identically whether PiKaraoke starts on
  boot or via a manual double-click) and marks it executable, since
  LXDE/PCManFM refuses to run a double-clicked `.desktop` file that isn't.

## [v0.6.0] - 2026-07-06

### 🚀 New Features

- **Restored `--deskpi` DeskPi Lite 4 driver installation**, previously
  present in an old tagged release and a since-diverged backup branch but
  missing from `install.py` on `dev`/`main`. New `src/deskpi.py`:
  Pi-4-only guard (`/proc/device-tree/model`), skips if already installed
  (`/usr/lib/deskpi` or `systemctl is-enabled deskpi.service` — the same
  markers `uninstall.py`/`uninstall_clean.py`'s `--deskpi` already tears
  down), clones `DeskPi-Team/deskpi_v1` into a fresh temp dir, runs its
  `install.sh`, cleans up after itself.
- `src/cli.py` gained `parse_args()` (`--deskpi`, `store_true`); `install.py`
  itself is unchanged and still flag-free — `cli.run()` parses args
  internally. When a fresh driver install may need a reboot, that's now
  recorded via `state.toml`'s `reboot_required` field, which activates the
  `pk_aliases` reboot-on-flag mechanism that has existed since the TOML
  state migration but had nothing setting it until now.

### 🛠 Improvements

- Deleted `requirements.txt`: its one dependency (`packaging>=24.0`) was
  already duplicated in `config.toml`'s `core` package list, and nothing in
  the repo actually installed from it — `install.py` installs from
  `config.toml` directly.
- Fixed two docs left stale by the earlier TOML-state migration:
  `README.md`'s Installer State Tracking section and `CLAUDE.md` still
  described the old flat state files instead of `state.toml`.

## [v0.5.1] - 2026-07-05

### 🛠 Improvements

- De-duplicated the flat-TOML state read/write logic that previously existed
  as two hand-kept-in-sync copies (`src/state.py` and an embedded copy in
  `assets/autostart_pikaraoke.py`). Both now use a single shared
  `assets/state_toml.py`: `src/state.py` imports it directly from the repo,
  and `copy_assets()` now also copies it to `$HOME` alongside
  `autostart_pikaraoke.py`/`pikaraoke_ui.py`, which imports it as a
  same-directory module — same pattern already used for `pikaraoke_ui`.
  No behavior change; removes a format-drift risk between the two copies.

## [v0.5.0] - 2026-07-05

### 🚀 New Features

- **Structured TOML config and state**, replacing hardcoded Python literals
  and flat single-value files:
  - New `config.toml` (repo root) holds the minimum Python version and the
    core/apt package lists; `src/constants.py` loads it via the stdlib
    `tomllib` reader.
  - `~/.deskpi-karaoke/{VERSION,.last_applied_sha_dev,PIKARAOKE_VERSION,.reboot_required}`
    are consolidated into one `~/.deskpi-karaoke/state.toml`, managed by
    `src/state.py`'s new `load_state()`/`save_state()`. Legacy flat files are
    removed automatically on first run after upgrading.
  - New `state_query.py` (repo root) — `get`/`set` CLI so the bash
    `pk_aliases` helper can read/write state without a TOML parser of its
    own. `assets/autostart_pikaraoke.py` keeps a small standalone duplicate
    of the read/write logic for the `pikaraoke_version` field it owns, since
    it runs outside the repo after being copied to `$HOME`.
- **Real logging** everywhere: `print()`/`print_h()` replaced by Python's
  `logging` module across `src/*.py`, `install.py`, `uninstall.py`,
  `uninstall_clean.py`, and `assets/pikaraoke_ui.py` (new
  `src/logging_config.py`, `print_h` renamed to `log_section`).
- **Log rotation** for the autostart launcher: the `pikaraoke` subprocess's
  raw output (`~/pikaraoke_output.log`) is now rotated by a system
  `logrotate` drop-in (`copytruncate`, installed by new `src/logs.py`); the
  launcher's own bookkeeping messages move to a separate
  `~/pikaraoke_launcher.log` via `logging.handlers.RotatingFileHandler`, so
  Python-side and system-side rotation never fight over the same file.

### ⚠️ Breaking / Upgrade Notes

- **Minimum Python raised to 3.11** (from 3.10), required for the stdlib
  `tomllib` reader. Raspberry Pi OS Bookworm already ships 3.11, so this is a
  no-op on the actual target hardware. CI matrix updated accordingly
  (dropped 3.10, added 3.11).
- Installer state file layout changed (see above) — existing installs pick
  up the new format automatically on the next `pk update`/`pk devupdate`.

## [v0.4.7] - 2026-07-05

### 🛠 Improvements

- Added a `pytest` suite under `tests/` covering every `src/` module (35 tests):
  platform checks, apt/Deno/venv orchestration, yt-dlp config, asset copying
  and shell-rc patching, git/state-file handling, and CLI exit-code mapping.
  Tests run safely on any machine — no real Pi, `apt`/`sudo`, or `$HOME`
  dotfiles touched; filesystem paths and subprocess calls are mocked.
- `src/*.py` now do `from src import constants` instead of importing
  individual names, so tests (and future code) can patch `src.constants.X`
  in one place. Import-style only — no behavior change.
- Added `black` + `flake8` lint tooling (`requirements-dev.txt`,
  `pyproject.toml`, `.flake8`), dev-only and separate from the installer's
  stdlib-only runtime dependencies.
- Added `.github/workflows/lint-and-test.yml`: runs `black --check`,
  `flake8`, and `pytest` on every push/PR to `main` and `dev` (Python 3.10
  and 3.12).
- Updated `README.md` with the new `src/`/`tests/` project structure, a CI
  status badge, and a **Testing & Linting** section.

## [v0.4.6] - 2026-07-05

### 🛠 Improvements

- Refactored `install.py` from a single procedural script into a modular `src/`
  package (`constants`, `shell`, `system`, `network`, `venv`, `assets`, `state`,
  `cli`). `install.py` is now a thin entry point.
- `uninstall.py` and `uninstall_clean.py` now share `safe_remove()` and
  `stop_service()` from `src/shell.py` instead of duplicating them.
- Added `.gitignore` for `__pycache__`/`*.pyc`.
- No behavior change: installer remains strictly idempotent, and
  `assets/autostart_pikaraoke.py` / `assets/pikaraoke_ui.py` are untouched
  standalone scripts (copied to `$HOME` and run outside the repo).

## [v0.3.5] - 2026-01-23

### 🚀 New Features

- **JavaScript runtime support for yt-dlp**
  - Automatically installs and configures **Deno** as a JS runtime
  - Ensures compatibility with recent YouTube extraction changes

### 🛠 Improvements

- Installer now guarantees `yt-dlp` is available to PiKaraoke via PATH
- Autostart launcher explicitly includes:
  - PiKaraoke virtual environment binaries
  - Deno binaries for JS execution
- Improved reliability for fresh installs and upgrades without manual fixes

### 🐛 Fixes

- Fixed PiKaraoke startup failure when `yt-dlp` was not discoverable
- Prevented missing formats caused by lack of JS runtime during extraction

### 📝 Notes

- This release responds to upstream YouTube changes that now require a JS runtime
- Recommended for **all users**, especially those experiencing download or playback issues

## [v0.3.4] 2024-08-13

### 🚀 New Features

- **Main branch version check**
  - Installer now runs only if the recorded installed version differs from the latest Git tag.
  - Version recorded in `~/.deskpi-karaoke/VERSION` after a successful main install.
  - Skips redundant installs/reboots when repo and version are unchanged.

- **Dev branch SHA check**
  - Removed version check for dev (since it changes frequently without formal version bumps).
  - Installer now runs only if `origin/dev` has new commits since last applied.
  - Tracks applied commit SHA in `~/.deskpi-karaoke/.last_applied_sha_dev`.

### 🛠 Improvements

- Unified branch sync logic with `_pk_sync_repo_branch`.
- Fast-forward only pulls to prevent unintended merges.
- Added `pk version` command:
  - Shows installed main version (from `VERSION` file)
  - Shows latest Git tag
  - Shows last applied dev SHA
- Optional reboot triggered only when `.reboot_required` exists (created by installer).

### ✅ Testing

- **Main branch**
  - No changes → installer skipped.
  - New tag → installer runs, updates `VERSION`.
- **Dev branch**
  - No new commits → installer skipped.
  - New commit → installer runs, updates `.last_applied_sha_dev`.
- Verified installer-triggered reboot works as expected.

### 📌 Next Steps

- Ensure `install.py` writes to `VERSION` on main installs.
- Ensure installer writes `.reboot_required` when reboot is necessary.
- Optional: add `pk forceupdate` to bypass gating for troubleshooting.

[v0.3.3] - 2024-08-12
🚀 New Features
🖥️ pk alias command suite for quick terminal access:

pk update – update installer from main branch & reboot

pk devupdate – update installer from dev branch & reboot

pk reboot – reboot the Raspberry Pi

pk help – list available commands

🪄 Automatic .pk_aliases install – now added and sourced in .bashrc/.zshrc during install

🛠️ Improvements
🧪 Dev branch detection – skips legacy uninstall step to prevent missing file errors

📂 Uninstall path fix – now correctly references uninstall.py using absolute path

📦 Dependency handling:

Ensure yt-dlp is installed in PiKaraoke venv to fix download/playback issues

Added Chromium package fallback (chromium-browser → chromium) for compatibility

🧹 Consolidated uninstall logic into a single clean block

🔍 Improved get_version() to differentiate between dev branch and tagged releases

📝 Notes
This release focuses on ease of updates and stability for dev builds

Recommended for all users, especially those running on the dev branch or updating from older versions
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
