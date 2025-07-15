#!/bin/bash

echo "🎤 Uninstalling PiKaraoke DeskPi4 setup..."

# 1. Stop any running instance
echo "🛑 Stopping PiKaraoke if running..."
pkill -f pikaraoke.py

# 2. Remove virtual environment
if [ -d "$HOME/.venv" ]; then
  echo "🧹 Removing virtual environment..."
  rm -rf ~/.venv
fi

# 3. Remove cloned repos (except songs)
echo "🗑️ Removing PiKaraoke code..."
rm -rf ~/pikaraoke
rm -rf ~/pikaraoke-deskpi4
rm -rf ~/deskpi_v1

# 4. Remove autostart shortcut
if [ -f "$HOME/.config/autostart/pikaraoke.desktop" ]; then
  echo "🚫 Removing autostart entry..."
  rm -f ~/.config/autostart/pikaraoke.desktop
fi

# 5. Remove system packages (optional/safe)
read -p "🧯 Remove system packages like ffmpeg and chromium? [y/N]: " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  sudo apt remove --purge ffmpeg chromium-browser chromium-chromedriver -y
  sudo apt autoremove -y
fi

# 6. Preserve song folder
echo "🎵 Keeping your ~/pikaraoke-songs folder intact."

echo "✅ Uninstall complete."
