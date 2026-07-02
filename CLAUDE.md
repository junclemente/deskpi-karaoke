# CLAUDE.md — deskpi-karaoke

## Purpose
Installer for [PiKaraoke](https://github.com/vicwomg/pikaraoke) on Raspberry Pi 4/5 + DeskPi Lite 4.
Installs PiKaraoke into a venv and sets up LXDE autostart so PiKaraoke launches after the desktop loads.
Internet detection and WiFi setup are handled by [raspi-portal](https://github.com/junclemente/raspi-portal),
which runs as a systemd service *before* the desktop session starts.

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
~/.pk_aliases               # Shell functions (copied from assets/, sourced in .bashrc/.zshrc)
~/.deskpi-karaoke/VERSION   # Last installed main tag (written by record_state())
~/.deskpi-karaoke/.last_applied_sha_dev  # Last applied dev SHA
~/.deskpi-karaoke/.reboot_required       # Flag: installer requests reboot
```

## Repo structure
```
install.py                  # Main installer — idempotent, safe to re-run
uninstall.py                # Standard uninstall
uninstall_clean.py          # Full uninstall, preserves song library
assets/
  autostart_pikaraoke.desktop  # LXDE desktop entry template (Exec= rewritten by installer)
  pk_aliases                   # Shell functions sourced into .bashrc/.zshrc
```

## How install.py works
1. Checks Python version and platform (soft checks, non-fatal)
2. `apt_install()` — installs ffmpeg, chromium, python3-venv, nodejs, npm, curl
3. `install_deskpi()` (optional, `--deskpi`) — installs DeskPi Lite 4 case drivers, Pi 4 only
4. `install_raspi_portal()` (optional, `--raspi-portal`) — clones and installs raspi-portal
5. `install_deno()` — installs Deno to `~/.deno/bin/` via curl installer
6. `ensure_venv()` — creates `~/.venv-pikaraoke`, installs pip/pikaraoke/yt-dlp/packaging
7. `install_ytdlp_config()` — writes `~/.config/yt-dlp/config` with `--js-runtimes deno`
8. `copy_assets()` — writes `~/.config/autostart/pikaraoke.desktop` (Exec= points at venv binary),
   installs pk_aliases
9. `record_state()` — writes VERSION (main) or .last_applied_sha_dev (dev) to state dir

## How boot works (with raspi-portal installed)
1. systemd starts `raspi-portal.service` (Before=graphical.target)
2. raspi-portal checks wlan0 for internet; if missing, stands up a WiFi hotspot + captive portal
3. Once internet is confirmed (or user picks standalone mode), raspi-portal exits
4. LXDE desktop session starts
5. LXDE reads `~/.config/autostart/pikaraoke.desktop`
6. Runs `~/.venv-pikaraoke/bin/pikaraoke` directly — no wrapper script, no internet check

## No boot-time update checking
PiKaraoke updates happen via `pk update` (manual or scheduled), not on every boot.
There is no wrapper script between LXDE autostart and the pikaraoke binary.

## pk_aliases commands
These are shell functions, not scripts. They only exist in interactive terminal sessions
(sourced from .bashrc). They do NOT run on boot.
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
- Do not add internet-checking or update logic to the LXDE autostart path — raspi-portal owns that
- Do not use systemd for autostart — this project uses LXDE Desktop autostart intentionally
- Do not run install.py as root — it installs into the user's home directory
