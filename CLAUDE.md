# CLAUDE.md — deskpi-karaoke

## Purpose
Automated installer and boot-time launcher for [PiKaraoke](https://github.com/vicwomg/pikaraoke) on Raspberry Pi 4/5 + DeskPi Lite 4. Handles install, autostart, and updates.

## Target environment
- Hardware: Raspberry Pi 4 (4GB+) or Pi 5
- OS: Raspberry Pi OS Bookworm Desktop (LXDE)
- User: `pi` (standard Pi user, has sudo)
- Python: 3.10+ required

## Branch strategy
- `main` — stable, tagged releases only. This is what the Pi pulls via `pk update`.
- `dev` — active development. Use `pk devupdate` on Pi to track this.
- Never commit directly to main. Merge from dev via PR, then tag.

## Key paths (on the Pi at runtime)
```
~/.venv-pikaraoke/          # Python venv; pikaraoke, yt-dlp, packaging installed here
~/.deno/bin/deno            # Deno runtime for yt-dlp JS extraction
~/.config/autostart/pikaraoke.desktop  # LXDE autostart entry (written by installer)
~/autostart_pikaraoke.py    # Boot launcher (copied from assets/ by installer)
~/pikaraoke_ui.py           # Tkinter notification helper (copied from assets/)
~/.pk_aliases               # Shell functions (copied from assets/, sourced in .bashrc/.zshrc)
~/.deskpi-karaoke/VERSION   # Last installed main tag (written by record_state())
~/.deskpi-karaoke/.last_applied_sha_dev  # Last applied dev SHA
~/.deskpi-karaoke/.reboot_required       # Flag: installer requests reboot
~/pikaraoke_output.log      # Runtime log from autostart_pikaraoke.py
```

## Repo structure
```
install.py                  # Main installer — idempotent, safe to re-run
uninstall.py                # Standard uninstall
uninstall_clean.py          # Full uninstall, preserves song library
assets/
  autostart_pikaraoke.py    # Boot launcher: waits for internet, updates, launches pikaraoke
  autostart_pikaraoke.desktop  # LXDE desktop entry template (Exec= rewritten by installer)
  pikaraoke_ui.py           # Tkinter popups (show_info, show_error)
  pk_aliases                # Shell functions sourced into .bashrc/.zshrc
```

## How install.py works
1. Checks Python version and platform (soft checks, non-fatal)
2. `apt_install()` — installs ffmpeg, chromium, python3-venv, nodejs, npm, curl
3. `install_deno()` — installs Deno to `~/.deno/bin/` via curl installer
4. `ensure_venv()` — creates `~/.venv-pikaraoke`, installs pip/pikaraoke/yt-dlp/packaging
5. `install_ytdlp_config()` — writes `~/.config/yt-dlp/config` with `--js-runtimes deno`
6. `copy_assets()` — copies autostart scripts, rewrites Exec= in .desktop file, installs pk_aliases
7. `record_state()` — writes VERSION (main) or .last_applied_sha_dev (dev) to state dir

## How autostart works on boot
1. LXDE reads `~/.config/autostart/pikaraoke.desktop`
2. Runs `~/.venv-pikaraoke/bin/python ~/autostart_pikaraoke.py`
3. Script manually sets PATH to include venv bin and deno bin (LXDE doesn't source .bashrc)
4. Polls for internet: 10s silent, then 30s with popup
5. On internet: launches `pikaraoke` binary via subprocess, logs to `~/pikaraoke_output.log`

## Known issue — auto-update on boot is not implemented
`autostart_pikaraoke.py` contains `mark_for_update()` which writes `~/.pikaraoke_update_pending` but **nothing reads or acts on this flag**. It is dead code. The fix is to replace it with a direct `pip install --upgrade pikaraoke yt-dlp` call after internet is confirmed, before launching.

## pk_aliases commands
These are shell functions, not scripts. They only exist in interactive terminal sessions (sourced from .bashrc). They do NOT run on boot.
- `pk update` — pulls main, runs install.py if tag changed
- `pk devupdate` — pulls dev, runs install.py if SHA changed
- `pk version` — shows installed version, latest tag, last dev SHA
- `pk reboot` — reboots Pi

## Update gating logic
- `pk update`: skips installer if `~/.deskpi-karaoke/VERSION` matches latest git tag
- `pk devupdate`: skips installer if `.last_applied_sha_dev` matches current `origin/dev` SHA
- install.py is idempotent — safe to re-run even if gating is bypassed

## What NOT to do
- Do not add nodejs/npm dependencies — yt-dlp JS runtime is Deno, not Node
- Do not modify `~/.config/autostart/pikaraoke.desktop` manually — it gets overwritten by install.py
- Do not source .bashrc or .profile inside autostart_pikaraoke.py — set PATH explicitly instead
- Do not use systemd for autostart — this project uses LXDE Desktop autostart intentionally
- Do not run install.py as root — it installs into the user's home directory