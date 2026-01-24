# 🎤 PiKaraoke Installer for Raspberry Pi 4 + DeskPi Lite 4

![Version](https://img.shields.io/github/v/tag/junclemente/deskpi-karaoke?label=version&style=flat-square)

> **NOTE**  
> This project is an active work in progress. Development happens on the **`dev` branch**.  
> **Stable, production-ready releases are tagged on `main`.**

This repository provides an automated, opinionated way to install  
[PiKaraoke](https://github.com/vicwomg/pikaraoke) on a **Raspberry Pi 4 or Pi 5** running  
**Raspberry Pi OS Bookworm (Desktop)**, optimized for the **DeskPi Lite 4** case.

It focuses on:
- reliability on reboot
- hands-off startup
- safe updates for both stable and dev users

---

## ✨ Features

- 💻 **One-command installation** (`install.py`)
- 🔁 **Automatic startup on boot** (Desktop autostart)
- 🌐 **Internet-aware launch**
  - waits for connectivity before starting PiKaraoke
  - user-friendly notifications if offline
- 📦 **Version-aware installer**
  - main branch installs are gated by Git tags
  - dev branch installs are gated by commit SHA
- 🧪 **Developer-friendly**
  - safe dev updates without version churn
- 🎶 **yt-dlp JS runtime support**
  - installs and configures **Deno** for modern YouTube playback

---

## 🧰 Hardware & Software Requirements

**Hardware**
- Raspberry Pi 4 (4 GB or larger) **or** Raspberry Pi 5
- Micro SD card (16 GB or larger)
- DeskPi Lite 4 case (recommended)

**Software**
- Raspberry Pi OS **Bookworm – Desktop**
- Internet connection (Ethernet or Wi-Fi)

> ℹ️  
> PiKaraoke’s own runtime requirements (Python, ffmpeg, codecs, etc.)  
> are maintained upstream:  
> 👉 https://github.com/vicwomg/pikaraoke

---

## 📂 Project Structure (dev branch)

```
deskpi-karaoke/
├─ install.py                # main installer
├─ uninstall.py              # standard uninstaller
├─ uninstall_clean.py        # full clean uninstaller
├─ assets/
│  ├─ autostart_pikaraoke.py       # waits for internet + launches PiKaraoke
│  ├─ autostart_pikaraoke.desktop  # LXDE autostart entry
│  ├─ pikaraoke_ui.py              # Tk-based notifications
│  └─ pk_aliases                   # helper terminal aliases
├─ CHANGELOG.md
├─ LICENSE
└─ README.md
```

**Planned**
```
raspi_portal/   # NetworkManager + captive portal for first-time Wi-Fi setup
```

---

## 🚀 Installation

Clone the repository and run the installer:

```bash
git clone https://github.com/junclemente/deskpi-karaoke.git
cd deskpi-karaoke
python3 install.py
```

The installer will:

- Install required system packages (ffmpeg, chromium, python venv tools, etc.)
- Create a Python virtual environment at:
  ```
  ~/.venv-pikaraoke
  ```
- Install PiKaraoke and supporting Python packages
- Install **Deno** for yt-dlp JavaScript extraction
- Copy runtime assets into the Pi user’s home directory:
  ```
  ~/autostart_pikaraoke.py
  ~/pikaraoke_ui.py
  ~/.config/autostart/pikaraoke.desktop
  ~/.pk_aliases
  ```

---

## 🔁 Autostart Behavior

On boot:

1. LXDE executes:
   ```
   ~/.config/autostart/pikaraoke.desktop
   ```
2. This launches:
   ```
   ~/.venv-pikaraoke/bin/python ~/autostart_pikaraoke.py
   ```
3. The launcher:
   - waits for internet connectivity
   - launches PiKaraoke once connected
   - logs output to:
     ```
     ~/pikaraoke_output.log
     ```

If no internet is detected, a user-friendly popup is shown.

---

## 🧪 Aliases & Ongoing Maintenance

During installation, the installer copies `pk_aliases` to your home directory and
automatically sources it from `.bashrc` and `.zshrc`.

Once installed, **`pk` commands can be run from any directory**, including your home
directory (`~`). You do **not** need to `cd` into the repo again after the initial setup.

### Available Commands

- `pk update`  
  Update the installer and PiKaraoke from the **main branch**  
  (stable releases only, via Git tags)

- `pk devupdate`  
  Update the installer from the **dev branch**  
  (tracks the latest commit SHA)

- `pk version`  
  Show:
  - Installed release tag (main)
  - Latest available tag
  - Last applied dev commit SHA

- `pk reboot`  
  Reboot the Raspberry Pi

- `pk help`  
  List all available `pk` commands

### 🔁 Recommended Workflow

- **Initial install:**  
  Clone the repo and run `python3 install.py`

- **After that:**  
  Use `pk` commands for all updates and maintenance  
  👉 **This is the preferred and safest way to keep the system up to date**

You generally do **not** need to manually pull the repo or rerun `install.py` unless:
- You are developing locally
- You are debugging installer behavior
- You intentionally want to bypass version/SHA gating

### Installer State Tracking

Installer state is tracked in:

```bash 
~/.deskpi-karaoke/VERSION # last installed release tag (main)
~/.deskpi-karaoke/.last_applied_sha_dev # last applied dev commit
~/.deskpi-karaoke/.reboot_required # optional reboot flag
```

This allows updates to be:
- Version-aware (main)
- Commit-aware (dev)
- Idempotent and safe

---

## 🧹 Uninstall

Standard uninstall:
```bash
python3 uninstall.py
```

Full clean uninstall (preserves song library):
```bash
python3 uninstall_clean.py
```

---

## 🛠️ Development Notes

- The **dev branch** may include unfinished or experimental changes.
- **Only tags on `main` are considered production releases.**
- Documentation-only changes do **not** require a new version tag.
- The installer is designed to be **idempotent and safe to re-run**.

---

## 📜 License

MIT — see [LICENSE](LICENSE).
