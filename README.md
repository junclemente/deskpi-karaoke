# 🎤 PiKaraoke Installer for Raspberry Pi 4 + DeskPi Lite 4

![Version](https://img.shields.io/github/v/tag/junclemente/deskpi-karaoke?label=version&style=flat-square)
![Status](https://img.shields.io/badge/status-WIP-yellow?style=flat-square)

> ⚠️ **Work in Progress**  
> This project is under active development. Features and behavior may change frequently until a stable release.

This repo provides an automated, Python-based installer for [PiKaraoke](https://github.com/vicwomg/pikaraoke) on a Raspberry Pi 4 with a DeskPi Lite 4 case running Raspberry Pi OS (Bookworm Desktop).

It includes:

- 💻 One-command installation via `install.py`
- 🐍 Fully Python-driven — no `.sh` scripts
- 🔁 Auto-starts PiKaraoke on boot after internet is detected

---

## 🧰 Hardware & Software Requirements

- [Raspberry Pi 4 (4 GB or larger)](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- Micro SD Card (at least 16 GB, 128GB or larger recommended )
- [DeskPi Lite 4 case](https://deskpi.com/products/new-deskpi-lite-set-top-box-for-raspberry-pi-4)
- [Raspberry Pi OS (Bookworm Desktop)](https://www.raspberrypi.com/software/operating-systems/)
  > **Do not use the Lite version** — Chromium is required
- [15W USB-C Power Supply](https://www.raspberrypi.com/products/type-c-power-supply/)

---

## 🚀 Installation

1. **Clone this repository**

   ```bash
   git clone -b dev https://github.com/junclemente/deskpi-karaoke.git
   cd deskpi-karaoke
   ```

2. **Run the installer**

   ```bash
   python3 install.py          # For general installs
   python3 install.py --deskpi  # For DeskPi Lite 4 users
   ```

---

## 📦 What the Installer Does

- Installs required system packages:
  - `ffmpeg`, `chromium-browser`, `python3-venv`, etc.
- Optionally installs DeskPi Lite 4 drivers
- Creates a virtual environment: `~/.venv-pikaraoke`
- Installs `pikaraoke` via `pip`
- Copies `pikaraoke_start.py` to `~/`
- Adds an autostart entry that launches PiKaraoke after internet is detected

---

## 🔁 Autostart Behavior

On boot, the system:

- Waits up to 30 seconds for internet
- If connected: runs `pikaraoke` inside the virtual environment
- Logs output to `~/pikaraoke_output.log`

> The startup script lives at: `~/pikaraoke_start.py`  
> It is launched via autostart from: `~/.config/autostart/pikaraoke.desktop`

---

## 📂 Project Structure

```
deskpi-karaoke/
├── install.py               # Main Python installer
├── uninstall.py             # Standard uninstaller (v0.3.0+ only)
├── uninstall_clean.py       # Legacy cleaner (removes all previous versions)
├── assets/
│   ├── pikaraoke_start.py     # Python-based startup script
│   └── pikaraoke.desktop      # Autostart config file
├── VERSION
└── README.md
```

---

## 🛠 Troubleshooting

- ❌ **No audio?**  
  Use `raspi-config` or the desktop's audio settings to switch to HDMI or analog output

- ❌ **Browser doesn’t load?**  
  Ensure `chromium-browser` is installed and accessible. The system must boot into the desktop environment.

---

## 🙌 Credits

- [vicwomg/pikaraoke](https://github.com/vicwomg/pikaraoke) — the original PiKaraoke project
- [DeskPi Team](https://deskpi.com/products/new-deskpi-lite-set-top-box-for-raspberry-pi-4) — for the DeskPi Lite 4 case and driver scripts

---

## 📃 License

MIT License. See the `LICENSE` file.
