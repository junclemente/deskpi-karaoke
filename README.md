# pi-karaoke-install
 
 - Raspberry Pi 4
 - Micro SD Card
 - Deskpi Lite 4

 ## Steps to install pikaraoke onto DeskPiLite
### Clone deskpi_v1 repository into raspberry pi.
```bash
git clone https://github.com/DeskPi-Team/deskpi_v1.git
```

### Install drivers
```bash
sudo ./deskpi_v1/install.sh
```

Once driver installation has completed, RPi will automatically reboot. 

###  Install pikaraoke following Github: [https://github.com/vicwomg/pikaraoke](https://github.com/vicwomg/pikaraoke)

#### Install required programs:
```bash
sudo apt-get install ffmpeg chromium-browser chromium-chromedriver -y
```

#### Install and activate `venv`
```bash
# Create a .venv directory in the homedir
python -m venv ~/.venv
# Activate your virtual environment
source ~/.venv/bin/activate
```
#### Install pikaraoke from PyPi via pip
```bash
pip install pikaraoke
```

### Autostart pikaraoke
```bash
mkdir ~/.config/autostart
touch ~/.config/autostart/pikaraoke.desktop
```
Edit the pikaraoke.desktop with the following:
```
[Desktop Entry]
Type=Application
Name=Pikaraoke
Exec=/home/pi/pikaraoke_start_script.sh
```

Since pikaraoke is installed in a virtual environment (.venv)

