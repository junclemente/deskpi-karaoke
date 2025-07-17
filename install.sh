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
echo "🛠️ Installing DeskPi Lite drivers..."
if ! systemctl list-units --type=service | grep -q deskpi; then
    if [ -d "/home/pi/deskpi_v1" ]; then
        echo "✅ DeskPi driver folder already exists, skipping clone."
    else
        git clone https://github.com/DeskPi-Team/deskpi_v1.git /home/pi/deskpi_v1
    fi
    cd /home/pi/deskpi_v1
    sudo ./install.sh || echo "⚠️ DeskPi install failed or already installed. Continuing..."
else
    echo "✅ DeskPi service is already running."
fi

### STEP 3: Install RaspiWiFi ###
echo "📡 Installing RaspiWiFi..."
if [ -d "/usr/lib/raspiwifi" ]; then
    echo "✅ RaspiWiFi already installed."
else
    git clone https://github.com/jasbur/RaspiWiFi.git /home/pi/RaspiWiFi
    cd /home/pi/RaspiWiFi
    sudo python3 initial_setup.py || echo "⚠️ RaspiWiFi setup encountered an issue. Continuing..."
fi

### STEP 4: Install system packages ###
echo "📦 Installing required system packages..."
sudo apt-get update
sudo apt-get install -y ffmpeg chromium-browser chromium-chromedriver zenity || echo "⚠️ Some packages failed to install. Continuing..."

### STEP 5: Setup Python virtual environment ###
echo "🐍 Setting up Python virtual environment..."
if [ -d "/home/pi/.venv" ]; then
    echo "✅ Virtual environment already exists."
else
    python3 -m venv /home/pi/.venv
fi

if [ -f "/home/pi/.venv/bin/activate" ]; then
  # shellcheck source=/home/pi/.venv/bin/activate
  source "/home/pi/.venv/bin/activate"
fi
pip install --upgrade pip
pip install pikaraoke || echo "⚠️ PiKaraoke install failed. Please install manually in the venv."

### STEP 6: Create Desktop shortcuts ###
echo "🖥️ Creating desktop shortcuts..."
DESKTOP_PATH="/home/pi/Desktop"

cat > "$DESKTOP_PATH/Start PiKaraoke.desktop" << EOF
[Desktop Entry]
Name=Start PiKaraoke
Comment=Launch PiKaraoke
Exec=lxterminal -e "bash -c 'source /home/pi/.venv/bin/activate && pikaraoke > /home/pi/pikaraoke_output.log 2>&1'"
Icon=utilities-terminal
Terminal=false
Type=Application
Categories=Application;Audio;
EOF

chmod +x "$DESKTOP_PATH/Start PiKaraoke.desktop"

echo "✅ Installation complete! You may reboot now."


### STEP 7: Copy autostart Wi-Fi launcher script from repo ###
echo "🚀 Copying PiKaraoke autostart Wi-Fi script..."
cp ./scripts/pikaraoke_start_script.sh /home/pi/pikaraoke_start_script.sh
chmod +x /home/pi/pikaraoke_start_script.sh


### STEP 8: Add autostart entry ###
echo "🧩 Adding PiKaraoke to system autostart..."
AUTOSTART_DIR="/home/pi/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/pikaraoke.desktop"

mkdir -p "$AUTOSTART_DIR"

cat > "$AUTOSTART_FILE" << EOF
[Desktop Entry]
Name=PiKaraoke Auto Start
Comment=Wait for Wi-Fi then start PiKaraoke
Exec=/home/pi/pikaraoke_start_script.sh
Type=Application
X-GNOME-Autostart-enabled=true
EOF

chmod +x "$AUTOSTART_FILE"


echo "✅ Installation complete! You may reboot now to start PiKaraoke automatically on boot."

echo "🔁 Rebooting in 10 seconds..."
sleep 10
sudo reboot

