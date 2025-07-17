#!/bin/bash
set -e

LOGFILE="/home/pi/pikaraoke_output.log"
MAX_WAIT=30
CHECK_INTERVAL=5
elapsed=0

echo "📡 Checking for Wi-Fi connection..." | tee -a "$LOGFILE"

# Show Zenity info popup while checking for Wi-Fi
(
  sleep 1
  zenity --info \
    --title="🔍 Searching for Wi-Fi..." \
    --text="Trying to connect to Wi-Fi...\n\nWaiting up to $MAX_WAIT seconds before fallback." \
    --timeout=$MAX_WAIT &
)

# Loop until connected or timeout
while ! iwgetid -r >/dev/null && [ $elapsed -lt $MAX_WAIT ]; do
  sleep $CHECK_INTERVAL
  elapsed=$((elapsed + CHECK_INTERVAL))
done

# If connected, launch PiKaraoke
if iwgetid -r >/dev/null; then
  echo "✅ Connected to Wi-Fi after $elapsed seconds." | tee -a "$LOGFILE"
  echo "🚀 Launching PiKaraoke..." | tee -a "$LOGFILE"
  if [ -f /home/pi/.venv/bin/activate ]; then
    # shellcheck source=/home/pi/.venv/bin/activate
    . /home/pi/.venv/bin/activate
  fi
  pikaraoke >> "$LOGFILE" 2>&1
else
  echo "❌ No Wi-Fi connection after $MAX_WAIT seconds." | tee -a "$LOGFILE"
  echo "📶 Opening Wi-Fi network selection window..." | tee -a "$LOGFILE"

  (
    zenity --warning \
      --title="No Wi-Fi Detected" \
      --text="No Wi-Fi detected.\nPlease connect to a Wi-Fi network to continue." \
      --timeout=10
  ) &

  sleep 1

  # Launch Wi-Fi network GUI
  nm-connection-editor &
fi

