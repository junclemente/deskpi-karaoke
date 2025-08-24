# 🎤 PiKaraoke Installer for Raspberry Pi 4 + DeskPi Lite 4

![Version](https://img.shields.io/github/v/tag/junclemente/deskpi-karaoke?label=version&style=flat-square)

_NOTE:_ This is still a continuing work in progress. Development happens in the **dev branch**, with stable tags released on **main**.

This repo provides an automated way to install [PiKaraoke](https://github.com/vicwomg/pikaraoke) on a Raspberry Pi 4 (Bookworm Desktop) with a DeskPi Lite 4 case.

It includes:

- 💻 One-command installation (`install.py`)
- 📡 Automatic Wi-Fi detection (future: `raspi_portal/`)
- 🔁 Auto-starting PiKaraoke on boot via autostart script
- 📦 Version-aware installer + safe auto-updater (main vs dev branch)

---

## 🧰 Hardware & Software Requirements

- Raspberry Pi 4 (4 GB or larger) or Pi 5
- Micro SD card (16 GB or larger)
- [DeskPi Lite 4 case](https://deskpi.com)
- Raspberry Pi OS Bookworm **Desktop**
- Internet connection (Ethernet or Wi-Fi)

---

## 📂 Project Structure (dev branch)

```
deskpi-karaoke/
├─ install.py                # main installer
├─ uninstall.py              # standard uninstaller
├─ uninstall_clean.py        # full clean uninstaller
├─ assets/
│  ├─ autostart_pikaraoke.py       # waits for internet + launches PiKaraoke
│  ├─ autostart_pikaraoke.desktop  # autostart entry for LXDE/Bookworm Desktop
│  ├─ pikaraoke_ui.py              # Tk-based notification helper
│  └─ pk_aliases                   # helper aliases for update/devupdate
├─ CHANGELOG.md
├─ LICENSE
└─ README.md
```

> Coming soon:  
> `raspi_portal/` — NetworkManager-based hotspot + Flask portal for first-time Wi-Fi setup.

---

## 🚀 Installation

Clone the repo and run the installer:

```bash
git clone https://github.com/junclemente/deskpi-karaoke.git
cd deskpi-karaoke
python3 install.py
```

The installer will:

- Install system packages (ffmpeg, chromium, pip/venv, etc.)
- Create a Python virtual environment at `~/.venv-pikaraoke`
- Install PiKaraoke (`pip install pikaraoke`)
- Copy assets to the Pi user’s home:
  - `~/autostart_pikaraoke.py`
  - `~/pikaraoke_ui.py`
  - `~/.config/autostart/pikaraoke.desktop`
  - `~/.pk_aliases` (sourced in `.bashrc`/`.zshrc`)

---

## 🔁 Autostart Behavior

- On boot, LXDE runs `autostart_pikaraoke.desktop`
- This launches:
  ```
  /home/pi/.venv-pikaraoke/bin/python /home/pi/autostart_pikaraoke.py
  ```
- Script waits for internet:
  - ✅ If found: launches PiKaraoke in the venv, logs to `~/pikaraoke_output.log`
  - ❌ If not found: shows Tk error popup after retries

---

## 🧪 Aliases

`pk_aliases` installs helper commands:

- `pk update` → update installer + PiKaraoke (main branch, tags only)  
- `pk devupdate` → update installer from dev branch (by commit SHA)

Installer state is tracked in:

```
~/.deskpi-karaoke/VERSION              # last installed release tag
~/.deskpi-karaoke/.last_applied_sha_dev # last applied dev commit
~/.deskpi-karaoke/.reboot_required      # optional reboot flag
```

---

## 🧹 Uninstall

```bash
python3 uninstall.py
# or for a full clean wipe:
python3 uninstall_clean.py
```

---

## 🛠️ Development Notes

- Dev branch may contain unfinished or experimental features (use at your own risk).
- Stable tags on main are intended for production installs.
- Future work (`raspi_portal/`) will handle Wi-Fi captive portal setup when no internet is detected.

---

## 📜 License

MIT — see [LICENSE](LICENSE).
