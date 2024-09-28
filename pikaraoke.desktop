#!/bin/bash

LOGFILE="/home/pi/pikaraoke_log.txt"

# Function to check for internet connectivity by pinging Google's DNS server
check_internet() {
    echo "Checking for internet connection..." | tee -a $LOGFILE
    if ping -c 1 8.8.8.8 &> /dev/null; then
        return 0  # Internet connection is available
    else
        return 1  # No internet connection
    fi
}

# Main logic to wait for an internet connection
while true; do
    if check_internet; then
        echo "Internet connection found! Launching pikaraoke..." | tee -a $LOGFILE
        zenity --info --text="Internet connection found! Launching Pikaraoke..." --timeout=1
        pikaraoke > /home/pi/pikaraoke_output.log 2>&1
        break  # Exit the loop once pikaraoke is launched
    else
        echo "No internet connection. Retrying in 15 seconds..." | tee -a $LOGFILE
        zenity --info --text="Pikaraoke cannot start without an internet connection" --timeout=14
        sleep 1 # Wait before checking again
    fi
done