#!/bin/bash
set -e

LOGFILE="/home/pi/pikaraoke_uninstall.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "🧹 PiKaraoke Uninstaller Starting..."
echo "🕒 Timestamp: $(date)"

### 1. Stop PiKaraoke if running
echo "🛑 Stopping PiKaraoke if running..."
pkill -f pikaraoke || echo "ℹ️ PiKaraoke not currently running."

### 2. Remove desktop shortcut
echo "🗑️ Removing desktop shortcut..."
rm -f /home/pi/Desktop/Start\\ PiKaraoke.desktop

### 3. Remove PiKaraoke virtual environment
echo "🧽 Removing Python virtual environment..."
rm -rf /home/pi/.venv

### 4. Remove RaspiWiFi
if [ -d "/usr/lib/raspiwifi" ]; then
  echo "🧹 Removing RaspiWiFi..."
  sudo python3 /usr/lib/raspiwifi/uninstall.python3 || echo "⚠️ RaspiWiFi uninstall script failed or not found."
  sudo rm -rf /usr/lib/raspiwifi
  sudo rm -rf /etc/raspiwifi
  sudo rm -rf /var/log/raspiwifi.log
else
  echo "ℹ️ RaspiWiFi not installed or already removed."
fi

### 5. Optional: remove DeskPi drivers
echo "⚠️ DeskPi drivers are not removed automatically. If you wish to remove them, run:"
echo "    sudo systemctl disable deskpi && sudo systemctl stop deskpi"

echo "✅ Uninstall complete!"
