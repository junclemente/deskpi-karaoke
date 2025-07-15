#!/bin/bash

LOGFILE="/home/pi/raspiwifi_setup.log"
RASPIFI_REPO="https://github.com/jasbur/RaspiWiFi.git"
INSTALL_DIR="/home/pi/RaspiWiFi"

echo "$(date): Starting RaspiWiFi setup..." | tee -a $LOGFILE

# Clone RaspiWiFi repo if not already present
if [ ! -d "$INSTALL_DIR" ]; then
    echo "📥 Cloning RaspiWiFi..." | tee -a $LOGFILE
    git clone $RASPIFI_REPO $INSTALL_DIR
else
    echo "📂 RaspiWiFi already cloned. Skipping..." | tee -a $LOGFILE
fi

cd $INSTALL_DIR || { echo "Failed to cd to $INSTALL_DIR"; exit 1; }

# Fix for Bookworm: unmask hostapd and enable it
echo "🔧 Ensuring hostapd is unmasked and enabled..." | tee -a $LOGFILE
sudo systemctl unmask hostapd
sudo systemctl enable hostapd

# Disable systemd-resolved if it conflicts with dnsmasq
echo "🔧 Disabling systemd-resolved if active..." | tee -a $LOGFILE
if systemctl is-active --quiet systemd-resolved; then
    sudo systemctl stop systemd-resolved
    sudo systemctl disable systemd-resolved
    sudo rm -f /etc/resolv.conf
    echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
fi

# Install dependencies
echo "📦 Installing RaspiWiFi dependencies..." | tee -a $LOGFILE
sudo apt-get update
sudo apt-get install -y dnsmasq hostapd python3-pip python3-flask git

# Run RaspiWiFi installer
echo "🚀 Running RaspiWiFi installer..." | tee -a $LOGFILE
sudo ./install.py

echo "✅ RaspiWiFi installation complete. Rebooting into AP mode..." | tee -a $LOGFILE
sudo reboot