#!/bin/bash
set -e

LOGFILE="/home/pi/pikaraoke_install.log"
exec > >(tee -a "$LOGFILE") 2>&1

echo "📦 PiKaraoke Installer Starting..."
echo "🕒 Timestamp: $(date)"

### STEP 1: Validate OS and hardware ###
echo "🔍 Checking OS and hardware..."
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script must be run on a Raspberry Pi."
    exit 1
fi

if ! uname -a | grep -qi "bookworm"; then
    echo "⚠️ Warning: You are not using Raspberry Pi OS Bookworm Desktop. Proceeding anyway..."
fi

### STEP 2: Install DeskPi Lite drivers ###
echo "🔧 Installing DeskPi Lite drivers..."
git clone https://github.com/DeskPi-Team/deskpi_v1.git ~/deskpi_v1
cd ~/deskpi_v1
sudo ./install.sh
cd ~
rm -rf ~/deskpi_v1

### STEP 3: Install required system packages ###
echo "📦 Installing dependencies..."
sudo apt-get update
sudo apt-get install -y ffmpeg chromium-browser chromium-chromedriver zenity python3-venv

### STEP 4: Set up virtual environment and install PiKaraoke ###
echo "🐍 Creating virtual environment..."
python3 -m venv ~/.venv
source ~/.venv/bin/activate
pip install --upgrade pip
pip install pikaraoke

### STEP 5: Set up autostart ###
echo "🧩 Installing autostart .desktop entry..."
mkdir -p ~/.config/autostart
cp ./assets/pikaraoke.desktop ~/.config/autostart/
chmod +x ~/.config/autostart/pikaraoke.desktop

### STEP 6: Copy launcher script ###
echo "📜 Copying startup script..."
cp ./scripts/pikaraoke_start_script.sh ~/pikaraoke_start_script.sh
chmod +x ~/pikaraoke_start_script.sh

echo "✅ Installation complete! Rebooting in 10 seconds..."
sleep 10
sudo reboot
