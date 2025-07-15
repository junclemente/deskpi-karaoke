#!/bin/bash

LOGFILE="/home/pi/pikaraoke_log.txt"
MAX_WAIT=30
WAIT_INTERVAL=5
ELAPSED=0

echo "$(date): Starting PiKaraoke startup script..." | tee -a $LOGFILE

check_wifi() {
    echo "$(date): Checking for internet connection..." | tee -a $LOGFILE
    if ping -c 1 8.8.8.8 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

while [ $ELAPSED -lt $MAX_WAIT ]; do
    if check_wifi; then
        echo "$(date): Internet connection found. Launching PiKaraoke..." | tee -a $LOGFILE
        zenity --info --text="Internet found! Launching PiKaraoke..." --timeout=2
        source /home/pi/.venv/bin/activate
        pikaraoke > /home/pi/pikaraoke_output.log 2>&1
        exit 0
    else
        echo "$(date): No internet. Retrying in $WAIT_INTERVAL seconds..." | tee -a $LOGFILE
        sleep $WAIT_INTERVAL
        ELAPSED=$((ELAPSED + WAIT_INTERVAL))
    fi
done

# If we reach here, no internet after waiting
echo "$(date): No internet after $MAX_WAIT seconds. Rebooting into RaspiWiFi mode..." | tee -a $LOGFILE
zenity --warning --text="No internet detected after ${MAX_WAIT}s. Rebooting into Wi-Fi setup mode..." --timeout=4

# Optional: run setup script before rebooting
if [ -f /home/pi/scripts/setup_raspiwifi.sh ]; then
    bash /home/pi/scripts/setup_raspiwifi.sh
fi

sudo reboot
