# Claude Code Guidelines — deskpi-karaoke

## Build, Install and Test Commands
- **Initial Installation:** `python3 install.py` (Creates `~/.venv-pikaraoke` and sets up system dependencies)
- **Standard Uninstall:** `python3 uninstall.py`
- **Full Clean Uninstall:** `python3 uninstall_clean.py`
- **Development Runtime:** Runs via the virtual environment interpreter: `~/.venv-pikaraoke/bin/python`

### Global Terminal Aliases (pk commands)
Once installed, maintenance and testing should be run using the built-in aliases from any directory:
- Update from main branch (stable tags): `pk update`
- Update from dev branch (latest commit SHA): `pk devupdate`
- Check environment versions: `pk version`

## Code Style & Architecture
- **Language:** 100% Python 3.
- **Environment Management:** Always isolate runtime dependencies inside the `~/.venv-pikaraoke` virtual environment. Do not install global pip packages.
- **OS Target:** Optimized strictly for Raspberry Pi OS **Bookworm (Desktop)** running on a Raspberry Pi 4 or 5 inside a DeskPi Lite case.
- **Entry Points:** - `install.py` handles system package setup (ffmpeg, chromium, deno, python3-venv). Accepts an optional `--deskpi` flag (parsed in `src/cli.py`) to also install DeskPi Lite 4 case drivers via `src/deskpi.py` (Pi 4 only, idempotent, skips if already installed).
  - `assets/autostart_pikaraoke.py` acts as the boot launcher via LXDE autostart (`~/.config/autostart/pikaraoke.desktop`).

## Development Principles
- **Idempotency:** The `install.py` script must remain strictly idempotent. Re-running the installer should safely verify, update, or skip existing components without wiping user configuration or destroying the song library.
- **State Management:** Installer state, version tracking, and applied git SHAs must be read from/written to the `~/.deskpi-karaoke/` state directory.
- **Network Awareness:** Any autostart or launch mechanisms must gracefully check for internet connectivity first and leverage `assets/pikaraoke_ui.py` (Tkinter UI notifications) to inform the user if offline before spawning the PiKaraoke background process.
- **Branch Strategy:** Production releases are gated strictly by Git tags on the `main` branch. Active, experimental development belongs exclusively on the `dev` branch.

## Versioning & Changelog
- The repo-root `VERSION` file is the source-of-truth project version (semver). It is distinct from the `version` field in `~/.deskpi-karaoke/state.toml`, the installer *state* file written by `record_state()` from `git describe --tags` on `main`.
- Any non-trivial commit to `dev` (new feature, fix, or structural refactor) should bump `VERSION` (patch for internal/refactor changes, minor for user-facing features, per semver) and add a matching entry at the top of `CHANGELOG.md`.
- Follow the existing `CHANGELOG.md` format: `## [vX.Y.Z] - YYYY-MM-DD` heading, then relevant `### 🚀 New Features` / `### 🛠 Improvements` / `### 🐛 Fixes` / `### 📝 Notes` subsections — omit sections that don't apply.
- Tags on `main` (which gate releases per Branch Strategy above) should match the `CHANGELOG.md`/`VERSION` value being released.