# 🎤 PiKaraoke Installer for Raspberry Pi 4 + DeskPi Lite 4

# PiKaraoke Installer for Raspberry Pi 4 + DeskPi Lite 4

![Version](https://img.shields.io/github/v/tag/junclemente/pikaraoke-deskpi4?label=version&style=flat-square)

Automated installer and launcher for PiKaraoke on Raspberry Pi 4 with DeskPi Lite.

This repo provides an automated way to install [PiKaraoke](https://github.com/vicwomg/pikaraoke) on a Raspberry Pi 4 with a DeskPi Lite 4 case running Raspberry Pi OS (Bookworm Desktop).

It includes:

- 💻 One-command installation
- 📡 Automatic Wi-Fi detection with fallback to RaspiWiFi setup mode
- 🔁 Auto-starting PiKaraoke on boot using a virtual environment

---

## 🧰 Hardware & Software Requirements

- Raspberry Pi 4
- Micro SD Card (16 GB or larger)
- DeskPi Lite 4 case
- Raspberry Pi OS (Bookworm Desktop)
  > **Do not use Lite** — Chromium is required

---

## 🚀 Installation Steps

1. **Clone this repository**

   ```bash
   git clone https://github.com/yourusername/pikaraoke.git
   cd pikaraoke
   ```

2. **Run the installer**

   ```bash
   chmod +x install.sh
   ./install.sh
   ```

3. The Pi will reboot once setup is complete.

---

## 📦 What the Installer Does

- Installs DeskPi Lite drivers
- Installs required packages:
  - `ffmpeg`, `chromium-browser`, `zenity`, `python3-venv`, etc.
- Sets up a Python virtual environment
- Installs `pikaraoke` via `pip`
- Installs autostart config
- Adds a smart Wi-Fi check:
  - Waits up to 30 seconds for an internet connection
  - If no Wi-Fi found, installs and reboots into [RaspiWiFi](https://github.com/jasbur/RaspiWiFi) setup mode (`http://10.0.0.1`)

---

## 🔁 Autostart Behavior

On boot, the system:

- Checks for an internet connection
- If connected: launches PiKaraoke
- If **not** connected within 30 seconds:
  - Runs `setup_raspiwifi.sh`
  - Reboots into hotspot mode (`raspiwifi-XXXX`)
  - Lets you connect from your phone and configure Wi-Fi

---

## 📂 Project Structure

```
pikaraoke/
├── install.sh                    # Main installer
├── scripts/
│   ├── pikaraoke_start_script.sh  # Launch logic with Wi-Fi check
│   └── setup_raspiwifi.sh         # RaspiWiFi fallback installer
├── assets/
│   └── pikaraoke.desktop          # Autostart config
└── README.md
```

---

## 🛠 Troubleshooting

- ❌ **No audio?**  
  Use `raspi-config` or desktop audio settings to select HDMI or analog output

- ❌ **Stuck on splash screen?**  
  Ensure `chromium-browser` is installed and not blocked by a proxy or firewall

---

## 🙌 Credits

- [vicwomg/pikaraoke](https://github.com/vicwomg/pikaraoke)
- [jasbur/RaspiWiFi](https://github.com/jasbur/RaspiWiFi)
- DeskPi Team for the hardware support

---

## 📃 License

MIT License. See `LICENSE` file.
