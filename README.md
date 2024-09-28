# pi-karaoke-install
 
 - Raspberry Pi 4
 - Micro SD Card
 - Deskpi Lite 4

 ## Steps to install pikaraoke onto DeskPiLite
### Clone deskpi_v1 repository into raspberry pi.
```
git clone https://github.com/DeskPi-Team/deskpi_v1.git
```

### Install drivers
```
sudo ./deskpi_v1/install.sh
```

Once installed, RPi will automatically reboot. 

###  Install pikaraoke following Github: [https://github.com/vicwomg/pikaraoke](https://github.com/vicwomg/pikaraoke)

#### Install required programs:
```
sudo apt-get install ffmpeg chromium-browser chromium-chromedriver -y
```

#### Install and activaet `venv`
```
# Create a .venv directory in the homedir
python -m venv ~/.venv
# Activate your virtual environment
source ~/.venv/bin/activate
```
#### Install pikaraoke from PyPi
```
pip install pikaraoke
```

